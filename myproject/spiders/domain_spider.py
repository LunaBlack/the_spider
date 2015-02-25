# -*- coding: utf-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy import log

from myproject.items import MyprojectItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class DomainSpider(CrawlSpider): #当url获取规则为“域名匹配及指定路径”
    name = "domainspider"
    number = 0

    def __init__(self):

        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix()
        self.linkmatrix.setroot(self.start_urls)

        domains = rs.readdomain()
        self.allowed_domains = domains[0]

        self.rules = [Rule( LinkExtractor(
            allow = domains[1],
            deny = domains[2],
            allow_domains = domains[0]
            ),
            follow=True, callback="parse_domain")]

        super(DomainSpider, self).__init__()


    def parse_domain(self, response):
        myitem = MyprojectItem()
        myitem['url'] = response.url
        myitem['referer'] = response.request.headers['Referer']
        try:
            response.selector.remove_namespaces()
            self.number = self.number + 1
    ##        self.log('A response from %s just arrived!' % response.url)
            myitem['idnumber'] = str(self.number)
            title_exp = response.xpath("//title/text()").extract()
            if title_exp:
                myitem['title'] = title_exp[0].strip()
            else:
                myitem['title'] = ''
            myitem['body'] = response.body
        except AttributeError:
            self.log("not TextResponse: {0}".format(type(response)), log.ERROR)
            myitem['title'] = ''
            myitem['body'] = response.body
        finally:
            return myitem

