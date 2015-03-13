# -*- coding: utf-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.http import Request
from scrapy.log import INFO
from scrapy.log import DEBUG
from scrapy.log import ERROR

from myproject.items import CrawledItem, PassItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class XpathSpider(CrawlSpider): #当url获取规则为“Xpath表达式”
    name = "xpathspider"

    def __init__(self):
        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        self.allowed_domains = rs.readalloweddomain()
        self.xpath = rs.readxpath()
        self.rules = [Rule(LinkExtractor(), follow=True, callback="parse_start_url")]

        super(XpathSpider, self).__init__()


    def parse_start_url(self, response):
        response.selector.remove_namespaces()
        self.log('receive response from {0}'.format(response.url), INFO)

        urls = response.xpath(self.xpath).extract()

        base_url = get_base_url(response)

        for e in urls:
            if not e.startswith("http://") and not e.startswith("https://"):
                url = urljoin_rfc(base_url, e)
            elif e.startswith("javascript:"):
                continue
            else:
                url = e
            self.log('queued a request to {0}'.format(url), INFO)
            yield Request(url, callback = self.parse_xpath_item)

        item = PassItem()
        item['url'] = response.url
        try:
            item['referer'] = response.request.headers['Referer']
        except KeyError as e:
            pass
        else:
            yield item


    def parse_xpath_item(self, response):
        self.log('receive xpath response from {0}'.format(response.url), INFO)
        response.selector.remove_namespaces()

        item = CrawledItem()
        item['url'] = response.url
        item['referer'] = response.request.headers['Referer']
        if 'redirect_urls' in response.meta:
            self.log("redirect_urls: {0}".format(repr(response.meta['redirect_urls'])), INFO)
        try:
            response.selector.remove_namespaces()
            title_exp = response.xpath("//title/text()").extract()
            if title_exp:
                item['title'] = title_exp[0].strip()
            else:
                item['title'] = ''
            item['body'] = response.body
        except AttributeError:
            self.log("not TextResponse: {0}".format(type(response)), ERROR)
            item['title'] = ''
            item['body'] = response.body
        finally:
            return item

