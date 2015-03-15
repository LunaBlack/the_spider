# -*- coding: utf-8 -*-

import re

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.http import TextResponse
from scrapy.log import INFO
from scrapy.log import ERROR

from myproject.items import CrawledItem, PassItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class MatchSpider(CrawlSpider): #当url获取规则为“域名匹配及指定路径”
    name = "matchspider"

    def __init__(self):

        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        self.allowed_domains = rs.readalloweddomain()
        allow, deny = rs.readurlmatch()

        self.regex_allow = re.compile('({0})'.format('|'.join(allow)))
        self.regex_deny = re.compile('({0})'.format('|'.join(deny)))

        self.rules = [Rule( LinkExtractor(), follow=True, callback="parse_domain")]

        super(MatchSpider, self).__init__()

    def parse_domain(self, response):
        self.log('receive response from {0}'.format(response.url), INFO)
        url = response.url

        if bool(self.regex_allow.search(url)):
            if not bool(self.regex_deny.search(url)):
                item = CrawledItem()
                item['url'] = response.url
                item['referer'] = response.request.headers['Referer']
                if isinstance(response, TextResponse):
                    response.selector.remove_namespaces()
                    title_exp = response.xpath("//title/text()").extract()
                    if title_exp:
                        item['title'] = title_exp[0].strip()
                    else:
                        item['title'] = ''
                    item['body'] = response.body
                yield item

        item = PassItem()
        item['url'] = response.url
        item['referer'] = response.request.headers['Referer']
        yield item

