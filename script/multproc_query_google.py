import argparse
import multiprocessing
import json
import sys
import re
import time

from googlesearch import search

reload(sys)
sys.setdefaultencoding('utf-8')

QUALITY_NUM = 5
PROCESS_NUM = 3

def collect_res(res):
    with open(args.output, 'w') as fout:
        for urls in res:
            fout.write("\n".join(["\t".join(t) for t in urls]))

def issue_request(query_num):
    urls = []
    time.sleep(1)
    idx = 1
    q, num = query_num
    for url in search(q, stop=3):
        print("[No. %s] %s" %(num, q))
        urls.append([q, url, str(idx)])
        idx += 1
    return urls

def deal_queries(fin):
    queries = []
    idx = 0
    for line in fin:
        g = line.strip("\n \t").split('\t')
        query = g[0]
        queries.append((query, idx))
        idx += 1
    pool = multiprocessing.Pool(processes=PROCESS_NUM)
    r = pool.map_async(issue_request, queries, callback=collect_res)
    r.wait()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--query')
    parser.add_argument('--output')
    args = parser.parse_args()
    with open(args.query) as fin:
        deal_queries(fin)
