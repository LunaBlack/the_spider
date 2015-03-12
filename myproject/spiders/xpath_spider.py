# -*- coding: utf-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request
from scrapy.log import INFO
from scrapy.log import ERROR

from myproject.items import MyprojectItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class XpathSpider(CrawlSpider): #当url获取规则为“Xpath表达式”
    name = "xpathspider"
    number = 0

    def __init__(self):
        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        domain, self.url = rs.readxpath()
        self.allowed_domains = domain
        self.rules = [Rule(LinkExtractor(), follow=True, callback="parse_start_url")]

        super(XpathSpider, self).__init__()


    def parse_start_url(self, response):
        response.selector.remove_namespaces()

        myitem_temp = MyprojectItem()
        myitem_temp['url'] = response.xpath(self.url).extract()

        base_url = get_base_url(response)
        url = ""

        if type(myitem_temp['url']) == list:
            for e in myitem_temp['url']:
                if not e.startswith("http://") and not e.startswith("https://"):
                    url = urljoin_rfc(base_url, e)
                else:
                    url = e
                yield Request(url, callback = self.parse_xpath_item)

        elif type(myitem_temp['url']) == str:
            if not myitem_temp['url'].startswith("http://") and not myitem_temp['url'].startswith("https://"):
                url = urljoin_rfc(base_url, myitem_temp['url'])
            else:
                url = myitem_temp['url']
            yield Request(url, callback = self.parse_xpath_item)


    def parse_xpath_item(self, response):
        self.log('receive response from {0}'.format(response.url), INFO)
        response.selector.remove_namespaces()

        myitem = MyprojectItem()
        myitem['url'] = response.url
        myitem['referer'] = response.request.headers['Referer']
        if 'redirect_urls' in response.meta:
            self.log("redirect_urls: {0}".format(repr(response.meta['redirect_urls'])), INFO)
        try:
            response.selector.remove_namespaces()
            title_exp = response.xpath("//title/text()").extract()
            if title_exp:
                myitem['title'] = title_exp[0].strip()
            else:
                myitem['title'] = ''
            myitem['body'] = response.body
        except AttributeError:
            self.log("not TextResponse: {0}".format(type(response)), ERROR)
            myitem['title'] = ''
            myitem['body'] = response.body
        finally:
            return myitem

