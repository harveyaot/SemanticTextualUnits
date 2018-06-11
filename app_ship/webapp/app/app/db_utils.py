import requests
import pymongo
import redis
import sys

DB = "comparison"
collection = 'raw_web'
test_collection= 'test'
SRC_DEMO_ONLINE = 'demo_online'

redis_host='stcgpu-20'
redis_port='6379'
db=5

tags = ['golden', 'cellphone']


def prepare_webs():
    conn = pymongo.MongoClient()
    webs = conn[DB][collection]
    return webs 

webs = prepare_webs()
save_judge_redis = redis.StrictRedis(redis_host, redis_port, db=db)
#golden_docs = webs.find({'is_golden':True})
golden_docs = webs.find()

def get_web_by_url(url, webs):
    web = None
    web = webs.find_one({'url':url})
    if web is not None:
        return web
    try:
        resp = requests.get(url)
        print >> sys.stderr, '[New Request] %s' % url
        content = resp.content
        web = {
                'url': url,
                'content': content,
                'is_golden': False,
                'src': SRC_DEMO_ONLINE
             }
        save_web_to_mongo(web, webs)
    except Exception as e:
        print >> sys.stderr, e
        pass
    return web

def save_web_to_mongo(web, webs):
    if web is None:
        return None
    post_id = webs.insert_one(web).inserted_id
    return post_id

def test_get_save():
    url = "https://www.forbes.com/sites/gordonkelly/2018/01/07/iphone-x-vs-iphone-8-vs-iphone-8-plus-whats-the-difference"
    web = get_web_by_url(url, webs)
    print "[web] is", web
    post_id = save_web_to_mongo(web, webs)
    print "[post_id] is", post_id


if __name__ == "__main__":
    test_get_save()

