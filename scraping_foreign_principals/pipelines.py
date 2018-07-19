# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


# pylint: disable=R0205, W0613, R0201, R0903
class ScrapingForeignPrincipalsPipeline(object):
    def process_item(self, item, spider):
        return item
