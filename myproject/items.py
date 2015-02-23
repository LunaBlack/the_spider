# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MyprojectItem(scrapy.Item):
    url = scrapy.Field()
    idnumber = scrapy.Field()
    title = scrapy.Field()
    body = scrapy.Field()
##    name = scrapy.Field()
##    description = scrapy.Field()
##    size = scrapy.Field()
