# -*- coding: utf-8 -*-
class TextUnit(object):
    """
    Object representing blocks of text which focus on one sub-topic, usually in
    the format of one topic in top and several paragraphs below.
    """ 
    def __init__(self, topic_paragraph=None):
        self.topic_paragraph = topic_paragraph
        self.paragraphs = []

    @property
    def topic_text(self):
        return self.topic_paragraph.text if self.topic_paragraph else ""

    @property
    def paragraphs_text(self):
        return "\n".join([p.text for p in self.paragraphs])

    @property
    def text(self):
        return self.topic_text + '\n' + self.paragraphs_text

    def __len__(self):
        text = len(self.text)
