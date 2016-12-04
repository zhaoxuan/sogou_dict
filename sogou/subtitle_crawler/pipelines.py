# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import urllib


class SubtitleCrawlerPipeline(object):
    def process_item(self, item, spider):
        try:
            file_name = urllib.unquote(item['filename'][0])
            fp = open('result/' + file_name, 'w')
            fp.write(item['body'])
            fp.close()
            return item
        except Exception, e:
            print e
