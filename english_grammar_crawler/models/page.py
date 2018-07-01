# -*- coding:utf-8 -*-


from .Bmob import BmobModel


class Page(BmobModel):

    article = {}
    postedAt = ''
    title = ''
    urlHash = ''
    viewCnt = 0
    url = ''
    hierDepth = 0
    ancestorTags = []
    parentTag = ''
    tag = ''
    pType = 0
    
    
