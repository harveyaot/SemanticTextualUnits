import sys 
import pymongo
import json
import redis

DB = "comparison"
collection = 'raw_web'

def prepare_webs():
    conn = pymongo.MongoClient("localhost",27016)
    webs = conn[DB][collection]
    return webs 

webs = prepare_webs()
docs = webs.find()


review_docs =  webs.find({'is_review':True})
comparison_docs =  webs.find({'is_cellphone':True})
print(review_docs.count())
print(comparison_docs.count())


def generate_answer_by_judge(tus, labels):
    res = []
    for tidx, label in enumerate(labels):
        finish = False
        if label and label.get('label', False):
            for pidx, p in enumerate(label.get('ps',[])):
                if p:
                    for sidx,sent in enumerate(p):
                        if sent:
                            topic = "".join(tus[tidx]['topic_paragraph']['sents'])
                            diff = tus[tidx]['paragraphs'][pidx]['sents'][sidx]
                            # only keep one sentence
                            finish = True
                            res.append({'aspect':topic, 'summary':diff})
                            break
                if finish:
                    break
    return res


def summary_doc(doc):
    judge_results = doc.get('judge_results', None)
    if judge_results is not None:
        labels = judge_results.get('labels', None)
        tus = judge_results.get('textunits', None)
        if labels and tus:
            answer = generate_answer_by_judge(tus, labels)
            url = doc.get('url', None)
            if url and len(answer) > 4 and len(answer) < 7:
                #return "%s\t%s" %(url, json.dumps(answer))
                return (url, json.dumps(answer))
    return None

import re
pat = re.compile('versus|-vs-')
count = 0
for doc in review_docs:
    res = summary_doc(doc)
    if res != None:
        if not pat.search(res[0]):
            print( "%s\t%s\t%s" %(res[0],'review', res[1]))
            count += 1
print count

count = 0
for doc in comparison_docs:
    res = summary_doc(doc)
    if res != None:
        print( "%s\t%s\t%s" %(res[0], 'comparison', res[1]))
        count += 1
print count
