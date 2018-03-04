import sys
import requests
import lxml.html as lh
from lxml import etree
import re
import redis

text_tag_pat = re.compile('^p$|^h[\d]{1}$|^b$|^br$')

conn = redis.StrictRedis()


def cache(func):
    def __wrapper__(url):
        if conn.get(url):
            html = conn.get(url)
        else:
            html = func(url)
        return html
    return __wrapper__


@cache
def get_html(url):
    resp = requests.get(url)
    html = resp.text
    return html

def get_title(html):
    doc = lh.fromstring(html)
    _title = doc.xpath("//title")
    if not _title:
        raise Exception("No title founded")
    title = _title[0].text
    return title

def get_body_html(html):
    doc = lh.fromstring(html)
    _body = doc.xpath("//body")
    if not _body:
        raise Exception("No body founded")
    body_html = etree.tostring(_body[0])
    return body_html

def split_into_stus(html):
    """ split the body_html into sementic textual units"""
    root = lh.fromstring(html)
    #print all tags to check
    #BFS to traverse
    #BFS_traverse(body)
    #DFS_traverse(body)
    divs = []
    DFS_traverse_for_stats(root, divs=divs)
    divs = sorted(divs, key=lambda x:x[1], reverse=True)
    for node, num  in divs:
        print "[DIV] [ID:{}][Class:{}][count:{}]".format(node.get('id'), node.get('class'), num)
    thres = 0 
    if len(divs) > 0:
        thres = divs[0][1]
    DFS_traverse_for_label(root, thres=thres) 
    new_html = etree.tostring(root)
    with open('tmp2.html', 'w') as fout:
        fout.write(new_html)

def DFS_traverse_for_label(node, num=0, thres=0):
    if type(node.tag) is str and  text_tag_pat.search(node.tag):
        return 1
    for c in node.getchildren():
        num += DFS_traverse_for_label(c, thres=thres)
    if node.tag == "div":
        if num >= thres:
            node.set('style', 'border:1px solid red')
        num = 0 
    return num


def DFS_traverse_for_stats(node, depth=0, num=0, divs=[]):
    if type(node.tag) is str and  text_tag_pat.search(node.tag):
        return 1
    for c in node.getchildren():
        num += DFS_traverse_for_stats(c, depth+1, divs=divs)
    if node.tag == "div":
        if num > 0:
            divs.append((node, num))
        num = 0
    return num

def DFS_traverse(node, depth=0):
    print "{} [Tag:{}][ID:{}][Class:{}]".format(" "*4* depth, node.tag, node.get('id'), node.get('class'))
    for c in node.getchildren():
        DFS_traverse(c, depth+1)

def BFS_traverse(node, depth=0):
    cur_nodes =  [node]
    next_nodes = []
    while cur_nodes:
        for c in cur_nodes:
            print " " * 4 * depth, c.tag
            for _c in c.getchildren():
                next_nodes.append(_c)
        cur_nodes = next_nodes
        next_nodes = []
        depth += 1

def test_get_url():
    default_url = "http://www.differencebetween.net/business/difference-between-public-administration-and-private-administration/"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    html = get_html(url)
    with open('tmp.html', 'w') as out:
        out.write(html.encode('utf-8'))

def test_get_title():
    with open('tmp.html') as fin:
        html = '\n'.join(fin.readlines())
    print get_title(html)

def test_get_body():
    with open('tmp.html') as fin:
        html = '\n'.join(fin.readlines())
        body_html = get_body_html(html)
        with open('body_tmp.html', 'w') as fout:
            fout.write(body_html)

def test_split_into_stus():
    default_url = "http://www.differencebetween.net/business/difference-between-public-administration-and-private-administration/"
    url = sys.argv[1] if len(sys.argv) > 1 else default_url
    html = get_html(url)
    split_into_stus(html)

if __name__ == "__main__":
    #test_get_url()
    #test_get_title()
    #test_get_body()
    #test_split()
    test_split_into_stus()
