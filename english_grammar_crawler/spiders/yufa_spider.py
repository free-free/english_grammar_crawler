# -*- coding: utf-8 -*-
import scrapy
import re
import json
import hashlib
from scrapy.http import Request
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from datetime import datetime
from urllib import parse
import functools

def extract_links(func):
    @functools.wraps(func)
    def _wrapper(obj, response):
        links = obj.link_extractor.extract_links(response)
        return func(obj, response, links)
    return _wrapper
        

def remove_crawled_links(func):
    @functools.wraps(func)
    def _wrapper(obj, response, links):
        return func(obj, response, links)
    return _wrapper
        

class YufaSpiderSpider(scrapy.spiders.CrawlSpider):
    name = 'yufa-spider'
    allowed_domains = ['www.yingyuyufa.com']
    start_urls = ['http://www.yingyuyufa.com/']
    # allow spider to crawl the same domain url except the url contained
    # 'www.yingyuyufa.com/plus/*'
    link_extractor = LinkExtractor(allow=("www.yingyuyufa.com[a-zA-Z0-9\/\.]+",), 
            deny=("www.yingyuyufa.com/plus/",))
    
    #rules = (
    #    Rule(LinkExtractor(allow=("www.yingyuyufa.com[a-zA-Z0-9\/\.]+",),
    #        deny=("www.yingyuyufa.com/plus",)),
    #        callback='parse_items',
    #        follow=False,
    #        process_links='filter_out_crawled_links'),
    #)
    
    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_links, errback=self.handle_http_err)


    def parse(self, response):
        pass

    def parse_article(self, response):
        article = {}
        page = {}
        article['title'] = response.xpath("//div[@class='article-title']/h1/text()").extract_first()
        info = response.xpath("//div[@class='article-title']//div[@class='writer']/span/text()").extract()
        article['author'] = info[0].split(":")[1].strip()
        article['source'] = info[1].split(":")[1].strip()
        article['date'] = info[2].split(":")[1].strip()
        content = response.xpath("//div[@class='content']/p")
        text = []
        for p in content:
            ptext = p.xpath(".//text()").extract()
            if '\xa0' in ptext:
                continue
            text.append(("".join(ptext)).rstrip())
        article['text'] = text
        page['article'] = article
        page['viewCnt'] = 0
        page['postedAt'] = str(datetime.strptime(article['date'],"%Y-%m-%d"))
        page['url'] = response.url
        page['title'] = response.meta['page_title']
        page['urlHash'] = hashlib.md5(response.url.encode("utf-8")).hexdigest()
        urlpath_parts = parse.urlsplit(response.url).path.strip("/").split("/")
        page['hierDepth'] = len(urlpath_parts)
        # filter out the items ending with 'html' or 'htm'
        # the left items serve as the parent tags of current page
        p_tags = list(filter(lambda item: not 
                re.match("[0-9a-zA-Z]+.((html)|(htm))", item), urlpath_parts))
        page['ancestorTags'] = p_tags
        page['parentTag'] = p_tags[-1]
        page['tag'] = urlpath_parts[-1]
        # pType = 0 represents article page
        # pType = 1 represents none article page
        page['pType'] = 0
        yield page


    @extract_links
    @remove_crawled_links
    def parse_links(self, response, links=tuple()):
        page = {}
        page['url'] = response.url
        page['title'] = response.meta.get('page_title','')
        page['urlHash']= hashlib.md5(response.url.encode('utf-8')).hexdigest()
        urlpath_parts = parse.urlsplit(response.url).path.strip("/").split("/")
        urlpath_parts = list(filter(lambda item: item != '', urlpath_parts))
        page['hierDepth'] = len(urlpath_parts)
        p_tags = list(filter(lambda item: not 
                re.match("[0-9a-zA-Z]+.((html)|(htm))", item), urlpath_parts))
        if len(p_tags) == 0:
            page['ancestorTags'] = ['.',]
            page['parentTag'] = '.'
            page['tag'] = '/'
        elif len(p_tags) == 1:
            page['ancestorTags'] = ['/',]
            page['parentTag'] = '/'
            page['tag'] = p_tags[-1]
        else:
            page['ancestorTags'] = p_tags
            page['parentTag'] = urlpath_parts[-2]
            page['tag'] = urlpath_parts[-1]
        page['pType'] = 1
        page['viewCnt'] = 0
        page['postedAt'] = str(datetime.now())
        yield page
        article_links = set(filter(self.filter_out_article_links, links))
        none_article_links = set(filter(self.filter_out_none_article_links, links))
        for link in article_links:
            yield Request(link.url, callback=self.parse_article, errback=self.handle_http_err,
                    meta={"page_title": link.text})
        for link in none_article_links:
            yield Request(link.url, callback=self.parse_links, errback=self.handle_http_err,
                    meta={'page_title': link.text})


    def filter_out_article_links(self, link):
        ret = re.fullmatch("http://www.yingyuyufa.com[a-zA-Z0-9\.\/]+((html)|(htm))+", link.url)
        if ret:
            return True
        return False


    def filter_out_none_article_links(self, link):
        ret = re.fullmatch("http://www.yingyuyufa.com[a-zA-Z0-9\.\/]+((html)|(htm))+", link.url)
        if ret:
            return False
        return True



    def handle_http_err(self, exception):
        pass
