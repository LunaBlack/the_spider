# -*- coding: utf-8 -*-


import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from myproject.items import MyprojectItem
from readsetting import ReadSetting


class AutoSpider(CrawlSpider): #当url获取规则为“从页面自动分析获取”
    name = "autospider"
    number = 0

    def __init__(self):
        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.rules = [Rule(LinkExtractor(), follow=True, callback="parse_auto")]
        ##scrapy.log("start autospider!")

        super(AutoSpider, self).__init__()


    def parse_auto(self, response):
        response.selector.remove_namespaces()
        self.number = self.number + 1
        ##self.log("A response from %s just arrived!" %response.url)
        myitem = MyprojectItem()
        myitem['url'] = response.url
        myitem['idnumber'] = str(self.number)
        myitem['title'] = response.xpath("//title/text()").extract()[0].strip()
        ##myitem['title'] = response.xpath("/a/text()").extract()
        ##myitem['name'] = response.xpath("//h1/text()").extract()
        ##myitem['description'] = response.xpath("//div[@id='description']").extract()
        ##myitem['size'] = response.xpath("//div[@id='info-left']/p[2]/text()[2]").extract
        return myitem
