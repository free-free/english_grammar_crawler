# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
from datetime import datetime
import hashlib
import re
import json

class GrammarSpiderSpider(scrapy.Spider):
    name = 'grammar-spider'
    allowed_domains = ['www.yingyuyufa.com']
    start_urls = ['http://www.yingyuyufa.com/']

    def start_requests(self):
        yield Request(self.start_urls[0], callback=self.parse_homepage)

    def parse_homepage(self, response):
        raw_categories = response.xpath("//div[@class='category']//div[@class='category-nav']//a")
        parsed_categories = []
        for cate in raw_categories:
            cate_name = cate.xpath(".//text()").extract_first()
            cate_url = cate.xpath("./@href").extract_first()
            cate_url = response.urljoin(cate_url)
            timestamp = datetime.now().timestamp()
            cate_dict = {}
            cate_dict['name'] = cate_name
            cate_dict['url'] = cate_url
            cate_dict['timestamp'] = timestamp
            need_hash_string = "{0}:{1}:{2}".format(cate_name,
                    cate_url,
                    timestamp).encode("utf-8")
            hashed_string = hashlib.md5(need_hash_string).hexdigest()
            cate_dict['md5_hash'] = hashed_string
            parsed_categories.append(cate_dict)
        yield {"categories": parsed_categories,"data_type":"meta"}
        for cate in parsed_categories:
            yield Request(cate['url'], callback=self.parse_category_page)
        
    def parse_category_page(self, response):
        raw_subcategories = response.xpath("//div[@class='category-index list-category-index']//h2/a")
        parsed_subcategories = []
        for item in raw_subcategories:
            item_name = item.xpath(".//text()").extract_first()
            item_url = item.xpath("./@href").extract_first()
            item_url = response.urljoin(item_url)
            timestamp = datetime.now().timestamp()
            item_dict = {}
            item_dict['name'] = item_name
            item_dict['url'] = item_url
            item_dict['timestamp'] = timestamp
            parsed_subcategories.append(item_dict)
        yield {"subcategories": parsed_subcategories, "data_type":"meta"}
        for subcate in parsed_subcategories:
            yield Request(subcate['url'],meta={'parent_node':subcate['name']})

    def parse(self, response):
        print(response.meta['parent_node'])
