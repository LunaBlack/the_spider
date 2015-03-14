# -*- coding: utf-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
#from scrapy.http import TextResponse
from scrapy import log

from myproject.items import CrawledItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix

class AutoSpider(CrawlSpider): #当url获取规则为“从页面自动分析获取”
    name = "autospider"
    number = 0

    def __init__(self): #读取setting文件内的各项参数
        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        self.allowed_domains = rs.readalloweddomain()
        self.rules = [Rule(LinkExtractor(), follow=True, callback="parse_auto")]
        ##scrapy.log("start autospider!")

        super(AutoSpider, self).__init__()


    def parse_auto(self, response):
        response.selector.remove_namespaces()
        
        myitem = CrawledItem()
        myitem['url'] = response.url
        myitem['referer'] = response.request.headers['Referer']

        #if isinstance(response, TextResponse):
        try:
            response.selector.remove_namespaces()
            self.number = self.number + 1
            ##self.log("A response from %s just arrived!" %response.url)
            myitem['idnumber'] = str(self.number)
            title_exp = response.xpath("//title/text()").extract()
            if title_exp:
                myitem['title'] = title_exp[0].strip()
            else:
                myitem['title'] = ''

            myitem['body'] = response.body
        #else:
        except AttributeError:
            self.log("not TextResponse: {0}".format(response.url), log.ERROR)
            myitem['title'] = ''
            myitem['body']= ''
        finally:
            return myitem

