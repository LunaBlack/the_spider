# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CrawledItem(scrapy.Item):
    url = scrapy.Field()
    referer = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()

class PassItem(scrapy.Item):
    url = scrapy.Field()
    referer = scrapy.Field()
