# -*- coding: utf-8 -*-


import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from myproject.items import MyprojectItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class DomainSpider(CrawlSpider): #当url获取规则为“域名匹配及指定路径”
    name = "domainspider"
    number = 0

    def __init__(self):

        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(self.start_urls)

        domains = rs.readdomain()

        #if rs.readdomain()[0] != ['']:
        #    self.allowed_domains = rs.readdomain()[0]
        if not (len(domains[0]) == 1 and domains[0][0] == ''):
            self.allowed_domains = domains[0]

        #if rs.readdomain()[2] != ('', ):
        if not (len(domains[2]) == 1 and domains[2][0] == ''):
            #self.rules = [Rule(LinkExtractor(allow = rs.readdomain()[1], deny = rs.readdomain()[2]), follow=True, callback="parse_domain")]
            self.rules = [Rule(LinkExtractor(allow = domains[1], deny = rs.readdomain()[2]), follow=True, callback="parse_domain")]
        else:
            self.rules = [Rule(LinkExtractor(allow = domains[1]), follow=True, callback="parse_domain")]

        super(DomainSpider, self).__init__()


    def parse_domain(self, response):
        response.selector.remove_namespaces()
        self.number = self.number + 1
##        self.log('A response from %s just arrived!' % response.url)
        myitem = MyprojectItem()
        myitem['url'] = response.url
        myitem['idnumber'] = str(self.number)
        myitem['title'] = response.xpath("//title/text()").extract()[0].strip()
        myitem['body'] = response.body
        myitem['referer'] = response.request.headers['Referer']

        return myitem

