# -*- coding: utf-8 -*-


import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from myproject.items import MyprojectItem
from readsetting import ReadSetting


class DomainSpider(CrawlSpider): #当url获取规则为“域名匹配及指定路径”
    name = "domainspider"

    number = 0
    rs = ReadSetting()
    start_urls = rs.readurl()
    
    if rs.readdomain()[0] != ['']:
        allowed_domains = rs.readdomain()[0]
    if rs.readdomain()[2] != ('', ):
        rules = [Rule(LinkExtractor(allow = rs.readdomain()[1], deny = rs.readdomain()[2]), follow=True, callback="parse_domain")]
    else:
        rules = [Rule(LinkExtractor(allow = rs.readdomain()[1]), follow=True, callback="parse_domain")]

        
    def parse_domain(self, response):
        response.selector.remove_namespaces()
        self.number = self.number + 1
##        self.log('A response from %s just arrived!' % response.url)
        myitem = MyprojectItem()
        myitem['url'] = response.url
        myitem['idnumber'] = str(self.number)
        myitem['title'] = response.xpath("//title/text()").extract()[0].strip()
##        myitem['title'] = response.xpath("//a/text()").extract()
##        myitem['name'] = response.xpath("//h1/text()").extract()
##        myitem['description'] = response.xpath("//div[@id='description']").extract()
##        myitem['size'] = response.xpath("//div[@id='info-left']/p[2]/text()[2]").extract
        return myitem
