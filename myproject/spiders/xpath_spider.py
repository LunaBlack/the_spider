# -*- coding: utf-8 -*-


import scrapy
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from myproject.items import MyprojectItem
from readsetting import ReadSetting


class XpathSpider(CrawlSpider): #当url获取规则为“Xpath表达式”
    name = "xpathspider"

    number = 0
    rs = ReadSetting()
    start_urls = rs.readurl()
    if rs.readxpath()[0] != ['']:
        allowed_domains = rs.readxpath()[0]
    rules = [Rule(LinkExtractor(), follow=True, callback="parse_start_url")]


    def parse_start_url(self, response):
        response.selector.remove_namespaces()
        
        myitem_temp = MyprojectItem()
        myitem_temp['url'] = response.xpath(self.rs.readxpath()[1]).extract()

        base_url = get_base_url(response)
        url = ""

        if type(myitem_temp['url']) == list:
            for e in myitem_temp['url']:
                if not e.startswith("http://") and not e.startswith("https://"):
                    url = urljoin_rfc(base_url, e)
                else:
                    url = e
                yield scrapy.Request(url, callback = self.parse_xpath_item)

        elif type(myitem_temp['url']) == str:
            if not myitem_temp['url'].startswith("http://") and not myitem_temp['url'].startswith("https://"):
                url = urljoin_rfc(base_url, myitem_temp['url'])
            else:
                url = myitem_temp['url']
            yield scrapy.Request(url, callback = self.parse_xpath_item)
    
    
##    def parse_xpath(self, response):
##        response.selector.remove_namespaces()
##            
##        myitem_temp = MyprojectItem()
##        myitem_temp['url'] = response.xpath(self.rs.readxpath()[1]).extract()
##
##        base_url = get_base_url(response)
##        url = ""
##        
##        if type(myitem_temp['url']) == list:
##            for e in myitem_temp['url']:
##                if not e.startswith("http://") and not e.startswith("https://"):
##                    url = urljoin_rfc(base_url, e)
##                else:
##                    url = e
##                yield scrapy.Request(url, callback = self.parse_xpath_item)
##
##        elif type(myitem_temp['url']) == str:
##            if not myitem_temp['url'].startswith("http://") and not myitem_temp['url'].startswith("https://"):
##                url = urljoin_rfc(base_url, myitem_temp['url'])
##            else:
##                url = myitem_temp['url']
##            yield scrapy.Request(url, callback = self.parse_xpath_item)



    def parse_xpath_item(self, response):
        response.selector.remove_namespaces()
        self.number = self.number + 1
        
        myitem = MyprojectItem()
        myitem['url'] = response.url
        myitem['idnumber'] = str(self.number)
        myitem['title'] = response.xpath("//title/text()").extract()[0].strip()
##        f = open("F:\Scrapy test\myproject\UI\html\item.txt", "a")
##        f.write(myitem['url'] + '\n' + str(response.meta['depth']) + '\n')       
        return myitem






##    def parse_xpath(self, response):
##        response.selector.remove_namespaces()
##        myitem_temp = MyprojectItem()
##        myitem_temp['url'] = response.xpath(self.rs.readxpath()[1]).extract()
##
##        myitems = []
##
##        base_url = get_base_url(response)
##
##        if type(myitem_temp['url']) == list:
##            myitem = MyprojectItem()
##            for e in myitem_temp['url']:
##                if not e.startswith('http://') and not e.startswith('https://'):
####                    yield scrapy.Request(urljoin_rfc(base_url, e), callback = self.parse_xpath_item)
##                    myitem['url'] = urljoin_rfc(base_url, e)
##                else:
####                    yield scrapy.Request(e, callback = self.parse_xpath_item)
##                    myitem['url'] = e
##                myitems.append(myitem)
##
##        elif type(myitem_temp['url']) == str:
##            if not myitem_temp['url'].startswith('http://') and not myitem_temp['url'].startswith('https://'):
####                yield scrapy.Request(urljoin_rfc(base_url, myitem_temp['url']), callback = self.parse_xpath_item)
##                myitem['url'] = urljoin_rfc(base_url, myitem_temp['url'])
##            else:
####                yield scrapy.Request(myitem_temp['url'], callback = self.parse_xpath_item)
##                myitem['url'] = myitem_temp['url']
##            myitems.append(myitem)
##
##        return myitems
##
####        return requests



##    def parse_xpath(self, response):
##        response.selector.remove_namespaces()
##        myitem_temp = MyprojectItem()
##        myitem_temp['url'] = response.xpath(self.rs.readxpath()[1]).extract()
##
##        base_url = get_base_url(response)
##
####        f = open("F:\Scrapy test\myproject\UI\html\item.txt", "a")
####        f.write('\n' + str(response.meta['depth']) + '\n' + response.url + '\n')
##
##        if type(myitem_temp['url']) == list:
##            for e in myitem_temp['url']:
##                if not e.startswith('http://') and not e.startswith('https://'):
####                    f = open("F:\Scrapy test\myproject\UI\html\item.txt", "a")
####                    f.write(urljoin_rfc(base_url, e) + '\n')
##                    yield scrapy.Request(urljoin_rfc(base_url, e), callback = self.parse_xpath_item)
##                else:
####                    f = open("F:\Scrapy test\myproject\UI\html\item.txt", "a")
####                    f.write(e + '\n')
##                    yield scrapy.Request(e, callback = self.parse_xpath_item)
##
##        elif type(myitem_temp['url']) == str:
##            if not myitem_temp['url'].startswith('http://') and not myitem_temp['url'].startswith('https://'):
##                yield scrapy.Request(urljoin_rfc(base_url, myitem_temp['url']), callback = self.parse_xpath_item)
##            else:
##                yield scrapy.Request(myitem_temp['url'], callback = self.parse_xpath_item)
