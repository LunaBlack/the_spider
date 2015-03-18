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


class MatchSpider(CrawlSpider): #当url获取规则为“网址匹配及指定路径”
    name = "matchspider"

    def __init__(self):

        rs = ReadSetting() #读取各项参数
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        self.allowed_domains = rs.readalloweddomain()
        allow, deny = rs.readurlmatch()

        self.regex_allow = re.compile('({0})'.format('|'.join([re.escape(e) for e in allow]))) #生成正则表达式
        self.regex_deny = re.compile('({0})'.format('|'.join([re.escape(e) for e in deny])))

        self.rules = [Rule( LinkExtractor(), follow=True, callback="parse_match")]
        #设置爬取规则:follow所有url;Request通过spidermiddlewares过滤掉限定域外的url;生成的response传递给parse_match
        #所有Request均经过spidermiddlewares

        super(MatchSpider, self).__init__()

    def parse_match(self, response):
        self.log('receive response from {0}'.format(response.url), INFO) #记录log,收到一个Response
        url = response.url

        item = PassItem() #所有传递到本函数中的Response,生成PassItem;即所有限定域内的url,生成一个PassItem
        item['url'] = response.url
        item['referer'] = response.request.headers['Referer']
        yield item
        
        if bool(self.regex_allow.search(url)): #判断url是否满足allow条件
            if not bool(self.regex_deny.search(url)): #判断url是否满足deny条件
                item = CrawledItem() #满足下载条件,则生成CrawledItem
                item['url'] = response.url
                item['referer'] = response.request.headers['Referer']
                if isinstance(response, TextResponse):
                    response.selector.remove_namespaces()
                    title_exp = response.xpath("//title/text()").extract() #提取网页title
                    if title_exp:
                        item['title'] = title_exp[0].strip()
                    else:
                        item['title'] = ''
                    item['body'] = response.body
                yield item


