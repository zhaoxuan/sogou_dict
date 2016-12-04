# coding:utf-8

import sys
import re
import logging
import commands

import scrapy
from subtitle_crawler.items import SubtitleCrawlerItem


reload(sys)
sys.setdefaultencoding("utf-8")

logger = logging.getLogger('SubTitleSpider')
# 老射手字幕
origin_url = "http://pinyin.sogou.com/dict/cate/index/%d"


class SubTitleSpider(scrapy.Spider):
    name = "subtitle"
    # 减慢爬取速度 为1s
    download_delay = 1

    allowed_domains = ["sogou.com"]
    start_urls = []

    for index in xrange(1, 500):
        next_url = origin_url % index
        start_urls.append(next_url)

    def parse(self, response):
        pages = response.selector.xpath('//div[@id="dict_page_list"]/ul/li/span/a/text()').extract()

        if len(pages) == 0:
            href = '/default'
            url = response.url + href
            request = scrapy.Request(url, callback=self.parse_list)
            yield request

        elif pages[-1] == '下一页':
            max_page = int(pages[-2])

            for i in range(1, max_page + 1):
                href = '/default/%s' % i
                url = response.url + href

                request = scrapy.Request(url, callback=self.parse_list)
                yield request
        else:
            print 'Unkown pages: ', pages

    def parse_list(self, response):
        detail_urls = response.selector.xpath('//div[contains(@class, "dict_detail_block")]/div[2]/div/a/@href').extract()

        for url in detail_urls:
            code, msg = commands.getstatusoutput('wget -q --content-disposition --tries=3 --directory-prefix=result/ "%s"' % (url))

        if code != 0:
            logger.info(msg)
            print url
        # request = scrapy.Request(url, callback=self.parse_file)
        # yield request

    def parse_file(self, response):
        filename = re.findall(r'attachment; filename="(.*)"', response.headers.get('Content-Disposition', ''))
        body = response.body
        item = SubtitleCrawlerItem()
        item['url'] = response.url
        item['body'] = body
        item['filename'] = filename
        return item
