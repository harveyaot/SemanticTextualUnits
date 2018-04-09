# -*- encoding: utf-8 -*-

import justext
import sys
import re
import lxml.html as lh

from textunit import TextUnit
from collections import namedtuple
from json import JSONEncoder

from nltk.tokenize import sent_tokenize
from nltk.tokenize import wordpunct_tokenize

PARAGRAPHS_NUM_MAX = 5
PARAGRAPHS_NUM_MIN = 0
TOPICS_NUM_MAX = 5

SubTopic = namedtuple('SubTopic', ['topic', 'content'])
Summary = namedtuple('Summary', ['title', 'subtopics'])

db_pat = re.compile(
                  r"difference[s]? between (.*?) and ([^!\?]*)",
                  re.IGNORECASE
                  )

pat_artical = re.compile("(^a |^an |^the )", re.IGNORECASE)
#db_pat = re.compile("difference.*between.*", re.IGNORECASE)
other_pat = re.compile("(.*?) +vs +(\S+.*)|(.*?) +or +(\S+.*)|(.*?) +and +(\S+.*)", re.IGNORECASE)
keywords = frozenset(['whereas', 'while', 'but', 'however', 'more', 'than', 'much', 'where'])

def splitParagraph(p):
    sents = sent_tokenize(p.text)
    p.sents = sents
    return p

class SummaryMaker(object):
    @classmethod
    def make_summary(cls, title, ts):
        subtopics = []
        for t in ts:
            topic = t.topic_paragraph.text
            content = cls._extract_comparison_sentence(title, t.paragraphs)
            if content:
                subtopics.append(SubTopic(topic, content))
        summary = Summary(title, subtopics[:TOPICS_NUM_MAX])
        return summary

    @classmethod
    def _extract_comparison_sentence(cls, title, paragraphs):
        """
        extract one or two sentence to clarify the main difference between two entities
        under this comparison topic
        """
        e1, e2 = cls._extract_entity(title)
        text = "".join([p.text for p in paragraphs])
        sent_scores = [[x, 0] for x in sent_tokenize(text)]
        # 
        for sent in sent_scores:
            if e1 and e1 in sent[0].lower():
                sent[1] += 1
            if e2 and e2 in sent[0].lower():
                sent[1] += 1
            for word in wordpunct_tokenize(sent[0]):
                if word.lower() in keywords:
                    sent[1] += 1
        sent_scores = sorted(sent_scores, key=lambda x:x[1], reverse=True)          
        #print sent_scores
        res = []
        if len(sent_scores) > 0 and sent_scores[0][1] > 0:
            res.append(sent_scores[0][0])
        if len(sent_scores) > 1 and sent_scores[1][1] == sent_scores[0][1]\
            and len(res) > 1 and len(res[0]) < 150:
            res.append(sent_scores[1][0])
        return " ".join(res)

    @classmethod
    def _extract_entity(cls, text):
        ea, eb = None, None
        if text == None:
            return ea, eb
        mat = db_pat.search(text)
        if mat:
            ea = mat.group(1).strip()
            eb = mat.group(2).strip()
        # other comparison scenario
        else :
            mat = other_pat.search(text)
            if mat:
                vals = [x for x in mat.groups() if x]
                assert len(vals) == 2
                ea = vals[0]
                eb = vals[1]
            else:
                return ea, eb 
        ea = pat_artical.sub("", ea).lower()
        eb = pat_artical.sub("", eb).lower()
        return ea, eb

class TextUnitMaker(object):
    @classmethod
    def _start_new_textunit(cls, textunit, textunits):
        if textunit is not None:
            textunits.append(textunit)

        textunit = TextUnit()
        return textunit

    @classmethod
    def partition(cls, ps):
        textunits = []
        textunit = None
        for p in ps:
            if p.is_boilerplate:
                continue
            if p.is_heading:
                textunit = cls._start_new_textunit(textunit, textunits)
                textunit.topic_paragraph = p 
            else:
                if textunit is None:
                    textunit = TextUnit()
                if len(p) > 3:
                    textunit.paragraphs.append(p)
        cls._start_new_textunit(textunit, textunits)
        return textunits

    @classmethod
    def filter(cls, ts):
        ts = [t for t in ts if t.topic_paragraph is not  None]
        #ts = filter(lambda t: len(t.paragraphs) > PARAGRAPHS_NUM_MIN and len(t.paragraphs) < PARAGRAPHS_NUM_MAX, ts)
        return ts


def paragraph2dict(p):
    d = p.__dict__
    d.update({'text':p.text,
        'is_heading':p.is_heading, 
        'is_boilerplate':p.is_boilerplate,
        "words_count":p.words_count
        })
    return d

def textunit2dict(t):
    d = t.__dict__
    for key, value in list(d.items()):
        if type(value) is list:
            value = list(map(paragraph2dict, value))
        else:
            value = paragraph2dict(value)
        d[key] = value
    return d

def summary2dict(s):
    d = s.__dict__
    for k, v in list(d.items()):
        if isinstance(v, list):
            for i, sub_v in enumerate(v):
                if isinstance(sub_v, tuple) and hasattr(sub_v, '_asdict'):
                    v[i] = sub_v.__dict__
    return d

def extract_title(html):
    title = None
    doc = lh.fromstring(html)
    elements = doc.xpath('//title')
    if elements:
        title = elements[0].text
    return title

def get_ts_for_url(url):
    import requests
    resp = requests.get(url)
    html = resp.content
    ps = justext.justext(html, justext.get_stoplist('English'))
    ts = TextUnitMaker.partition(ps)
    return ts

if __name__ == "__main__":
    ts = get_ts_for_url('http://www.wisegeek.org/what-is-the-difference-between-a-crocodile-and-an-alligator.htm#didyouknowout')
    for t in ts:
        print("********[topic:{}]***********".format(t.topic_text))
        print(t.paragraphs_text)
