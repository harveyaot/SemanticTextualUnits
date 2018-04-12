# -*- coding: utf-8 -*-


class TextualUnit(object):
    """
    Object representing blocks of text which focus on one sub-topic, usually in
    the format of one topic in top and several paragraphs below.
    """ 
    def __init__(self, topic_paragraph, paragraphs):
        self.topic_paragraph = topic_paragraph
        self.paragraphs = paragraphs

    @property
    def topic(self):
        return self.topic_paragraph.text

    @property
    def text(self):
        return "\n".join([p.text for p in self.paragraphs])
