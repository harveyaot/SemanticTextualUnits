#! /usr/bin/env python3
import sys
import redis
import pymongo
import collections
import json
import random
import time
import datetime

from random import shuffle
from flask import Flask, send_file
from flask import request
from flask_cors import CORS, cross_origin
from lxml.html.clean import Cleaner
from bson import json_util

import app.justext
from app.core import *

random.seed(int(time.time()))


app = Flask(__name__)
CORS(app)
DB = "comparison"
collection = 'raw_web'

mongo_host='localhost'
mong_port=27017
redis_host='localhost'
redis_port=6379
db=5
tags = ['golden', 'cellphone']

def prepare_webs():
    conn = pymongo.MongoClient(host=mongo_host, port=27017)
    webs = conn[DB][collection]
    return webs 

webs = prepare_webs()
golden_docs = webs.find({'is_cellphone':True})
#golden_num = webs.find({'is_cellphone':True}).count()
save_judge_redis = redis.StrictRedis(redis_host, redis_port, db=db)

def get_judges_num():
    return save_judge_redis.dbsize()

@app.route('/statistic', methods=['POST'])
def statistic():
    json_d = request.json
    name = json_d['signature']
    return json.dumps(
            { "querysets":
                [  
                    {
                        'name': tag, 
                        'total': webs.find({"is_%s"%tag:True}).count(),
                        'judged': webs.find({"is_%s"%tag:True, 'judge_results':{'$ne':None}}).count(),
                        'judgedByYou':webs.find({"is_%s"%tag:True, 'judge_results.judge':name}).count()
                    }
                    for tag in tags
                ]
            }
        )

@app.route('/load_judge', methods=['POST'])
def load_judge():
    json_d = request.json
    key = json_d['url']
    doc = webs.find_one({"url":key})
    judge_results = None
    if doc:
        judge_results = doc.get('judge_results', None)
    return json.dumps(judge_results)

@app.route('/save_judge', methods=['POST'])
def save_judge():
    json_d = request.json
    update_time = time.time
    if json_d is None:
        print('[None!]', file=sys.stderr)
        return json.dumps({'success':False})
    key = json_d['url']
    doc = webs.find_one({"url":key})

    if not doc:
        return json.dumps({'success':False})

    json_d['last_update'] = datetime.datetime.utcnow()
    res = webs.update_one(
            {'_id': doc['_id']},
            {
                "$set":{
                    "judge_results":json_d
                    }
            }
        )
    print(res.upserted_id)
    return json.dumps({'success':True})

@app.route('/clear_judge', methods=['POST'])
def clear_judge():
    json_d = request.json
    if json_d is None:
        print('[None!]', file=sys.stderr)
        return json.dumps({'success':False})
    key = json_d['url']
    doc = webs.find_one({"url":key})

    if not doc:
        return json.dumps({'success':False})

    res = webs.update_one(
            {'_id': doc['_id']},
            {
                "$set":{
                    "judge_results":None
                    }
            }
        )
    print(res.upserted_id)
    return json.dumps({'success':True})

@app.route('/random_one', methods=['POST'])
def random_one():
    params = request.json
    print (params)
    url_type = params.get('type')
    tag_idx = params.get('tagidx')
    signature = params.get('signature')
    queryNum = webs.find({"is_%s" %tags[int(tag_idx)]:True, 'judge_results':None}).count()
    judgeQueryNum = webs.find({"is_%s"%tags[int(tag_idx)]:True,'judge_results.judge':signature}).count()
    url = None
    print (queryNum, judgeQueryNum)
    if url_type == 1 and judgeQueryNum > 0:
        doc = webs.find({"is_%s"%tags[int(tag_idx)]:True,'judge_results.judge':signature})[random.randrange(judgeQueryNum)]
        url = doc['url'] if doc else None
    if url_type == 0 and queryNum > 0:
        doc = webs.find({"is_%s"%tags[int(tag_idx)]:True, 'judge_resutls':None})[random.randrange(queryNum)]
        url = doc['url'] if doc else None
    return json.dumps({'url': url})

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    params = request.json if request.json else request.args
    url = params.get('url')
    print("[Url] : %s" % url, file=sys.stderr)
    doc = webs.find_one({'url':url})
    if doc is None:
        print("return None", file=sys.stderr)
        return json.dumps(None)
    else:
        content = doc['content']
        ps = justext.justext(content, justext.get_stoplist('English'), preprocessor=preprocessor)
        ps_split = list(map(splitParagraph, ps))
        ps_dicts = list(map(paragraph2dict, ps))

        judge_results = doc.get('judge_results', None)
        labels, judge, last_update = None, None, None
        title = extract_title(content)
        # if already has been judged:
        if judge_results:
            print ('[Labeled]')
            ts_dicts = judge_results.get('textunits', None)
            labels = judge_results.get('labels', None)
            summary = SummaryMaker.make_summary_by_judge(title, ts_dicts, labels)
            summary_dicts = summary2dict(summary)
            judge = judge_results.get('judge', None)
            last_update = judge_results.get('last_update', None)
        else:
            # if it's has been judged before use judge
            ts = TextUnitMaker.partition(ps_split)
            ts = TextUnitMaker.filter(ts)
            summary = SummaryMaker.make_summary(title, ts)
            summary_dicts = summary2dict(summary)
            ts_dicts = list(map(textunit2dict, ts))

        return json.dumps({"paragraphs":ps_dicts,
            "textunits": ts_dicts,
            "summary": summary_dicts,
            "labels": labels,
            "judge": judge,
            "last_update": last_update
            }, default=json_util.default)

def preprocessor(dom):
    "Removes unwanted parts of DOM."
    options = {
        "processing_instructions": False,
        "remove_unknown_tags": False,
        "safe_attrs_only": False,
        "page_structure": False,
        "annoying_tags": False,
        "frames": True,
        "meta": False,
        "links": False,
        "javascript": False,
        "scripts": True,
        "comments": True,
        "style": True,
        "embedded": True,
        "forms": True,
        "kill_tags": ("head", "table"),
    }
    cleaner = Cleaner(**options)
    return cleaner.clean_html(dom)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5904)
    #print (statistic())
