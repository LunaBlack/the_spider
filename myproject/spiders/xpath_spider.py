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
        rs = ReadSetting() #读取各项参数
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        self.allowed_domains = rs.readalloweddomain()
        self.xpath = rs.readxpath()
        self.rules = [Rule(LinkExtractor(), follow=True, callback="parse_start_url")]
        #设置爬取规则:follow所有url;Request通过spidermiddlewares过滤掉限定域外的url;生成的response传递给parse_start_url
        #所有Request均经过spidermiddlewares

        super(XpathSpider, self).__init__()


    def parse_start_url(self, response): #提取xpath中的url,生成新的Request,得到的Response传递给parse_xpath_item
        response.selector.remove_namespaces()
        self.log('receive response from {0}'.format(response.url), INFO) #记录log,收到一个Response

        urls = response.xpath(self.xpath).extract() #提取符合xpath规则的url

        base_url = get_base_url(response) #提取Response中的url,补全相对地址前面省略的部分(部分xpath中的url为相对地址)

        for e in urls: #判断符合xpath规则的url是否为相对地址:若是,则补全为绝对地址
            if not e.startswith("http://") and not e.startswith("https://"):
                url = urljoin_rfc(base_url, e)
            elif e.startswith("javascript:"):
                continue
            else:
                url = e
            self.log('queued a request to {0}'.format(url), INFO) #记录log,生成一个Request
            yield Request(url, callback = self.parse_xpath_item) #针对符合xpath规则的url,生成Request,得到的Response传递给parse_xpath_item

        item = PassItem() #所有传递到本函数中的Response,生成PassItem;即所有限定域内的url,生成一个PassItem
        item['url'] = response.url
        try:
            item['referer'] = response.request.headers['Referer']
        except KeyError as e:
            pass
        else:
            yield item


    def parse_xpath_item(self, response): #针对xpath中的url(已经过spidermiddlewares过滤),生成CrawledItem
        self.log('receive xpath response from {0}'.format(response.url), INFO) #记录log,收到一个Response
        response.selector.remove_namespaces()

        item = CrawledItem()
        item['url'] = response.url
        item['referer'] = response.request.headers['Referer']
        
        if 'redirect_urls' in response.meta: #若此条response是被重定向过的
            self.log("redirect_urls: {0}".format(repr(response.meta['redirect_urls'])), INFO) #记录重定向信息(repr指以字符串形式返回)
            
        try:
            response.selector.remove_namespaces()
            title_exp = response.xpath("//title/text()").extract() #提取网页title
            if title_exp:
                item['title'] = title_exp[0].strip()
            else:
                item['title'] = ''
            item['body'] = response.body
        except AttributeError: #网页中找不到title
            self.log("not TextResponse: {0}".format(type(response)), ERROR)
            item['title'] = ''
            item['body'] = response.body
        finally:
            return item

