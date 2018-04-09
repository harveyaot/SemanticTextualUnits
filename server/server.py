#! /usr/bin/env python3
import sys
import redis
import pymongo
import collections
import json
import random
import time

from random import shuffle
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
from lxml.html.clean import Cleaner

import justext
from core import *

random.seed(int(time.time()))


app = Flask(__name__)
CORS(app)
DB = "comparison"
collection = 'raw_web'

redis_host='stcgpu-20'
redis_port='6379'
db=5

def prepare_webs():
    conn = pymongo.MongoClient()
    webs = conn[DB][collection]
    return webs 

webs = prepare_webs()
golden_docs = webs.find({'is_golden':True})
golden_num = webs.find({'is_golden':True}).count()


save_judge_redis = redis.StrictRedis(redis_host, redis_port, db=db)

def get_judges_num():
    return save_judge_redis.dbsize()

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


@app.route('/statistic', methods=['GET'])
def statistic():
    return json.dumps({'total_num':golden_num, 'judged_num':get_judges_num()})

@app.route('/load_judge', methods=['POST'])
def load_judge():
    json_d = request.json
    key = json_d['url']
    value = save_judge_redis.get(key)
    return value

@app.route('/save_judge', methods=['POST'])
def save_judge():
    json_d = request.json
    if json_d is None:
        print('[None!]', file=sys.stderr)
        return json.dumps({'success':False})
    key = json_d['url']
    labels = json_d['labels']
    save_judge_redis.set(key, json.dumps(json_d))
    return json.dumps({'success':True})

@app.route('/random_one', methods=['GET'])
def random_one():
    params = request.args
    url_type = params.get('type')
    url = None
    if url_type == "1":
        url = save_judge_redis.randomkey()
        url = url.decode('utf-8')
    else:
        # use unjuged
        keys = set(save_judge_redis.keys())
        a = list(range(golden_num))
        shuffle(a)
        for i in a:
            doc = golden_docs[i]
            url = doc['url']
            if url not in keys:
                break
    return json.dumps({'url': url})

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    params = request.json if request.json else request.args
    url = params.get('url')
    print("[Url] : %s" % url, file=sys.stderr)
    web = webs.find_one({'url':url})
    if web is None:
        print("return None", file=sys.stderr)
        return json.dumps(None)
    else:
        content = web['content']
        ps = justext.justext(content, justext.get_stoplist('English'), preprocessor=preprocessor)
        ps_split = list(map(splitParagraph, ps))
        ts = TextUnitMaker.partition(ps_split)
        ts = TextUnitMaker.filter(ts)
        title = extract_title(content)
        summary = SummaryMaker.make_summary(title, ts)
        summary_dicts = summary2dict(summary)
        ts_dicts = list(map(textunit2dict, ts))
        ps_dicts = list(map(paragraph2dict, ps))

        return json.dumps({"paragraphs":ps_dicts,
            "textunits": ts_dicts,
            "summary": summary_dicts,
            })
    return json.dumps(val)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5900)
