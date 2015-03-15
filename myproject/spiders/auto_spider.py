# -*- coding: utf-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
##from scrapy.http import TextResponse
from scrapy.log import INFO
from scrapy.log import ERROR

from myproject.items import CrawledItem, PassItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class AutoSpider(CrawlSpider): #当url获取规则为“从页面自动获取”
    name = "autospider"

    def __init__(self):

        rs = ReadSetting() #读取各项参数
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        self.rules = [Rule( LinkExtractor(), follow=True, callback="parse_auto")]
        #设置爬取规则:follow所有url;Request通过spidermiddlewares过滤掉限定域外的url;生成的response传递给parse_auto
        #所有Request均经过spidermiddlewares
        
        super(AutoSpider, self).__init__()

    def parse_auto(self, response):
        self.log('receive response from {0}'.format(response.url), INFO) #记录log,收到一个Response
        response.selector.remove_namespaces()

        item = CrawledItem() #所有传递到本函数中的Response.url,均满足抓取下载条件;即所有限定域内的url,生成一个CrawledItem
        item['url'] = response.url
        item['referer'] = response.request.headers['Referer']
        
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
            yield item

        item = PassItem() #所有传递到本函数中的Response,生成PassItem;即所有限定域内的url,生成一个PassItem
        item['url'] = response.url
        item['referer'] = response.request.headers['Referer']
        yield item

