# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawledItem(scrapy.Item): #定义抓取下载的条目
    url = scrapy.Field()
    referer = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()

class PassItem(scrapy.Item): #定义爬取到的、但不属于抓取下载范围的条目
    url = scrapy.Field()
    referer = scrapy.Field()
