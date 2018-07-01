# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


from .models.Bmob import BmobSDK
from .models.page import Page


class EnglishGrammarCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class BmobStoragePipeline(object):


    def __init__(self, bmob_app_id, bmob_rest_api_key):
        self._app_id = bmob_app_id
        self._rest_api_key = bmob_rest_api_key
        BmobSDK.setup(self._app_id, self._rest_api_key)



    def process_item(self, item, spider):
        page = Page(**item)
        page.save()
        return item


    def open_spider(self, spider):
        pass

    
    def close_spider(self, spider):
        pass


    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            crawler.settings.get("BMOB_APP_ID"),
            crawler.settings.get("BMOB_REST_API_KEY"))


