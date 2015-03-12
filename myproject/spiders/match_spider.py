# -*- coding: utf-8 -*-


from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from scrapy.log import INFO
from scrapy.log import ERROR

from myproject.items import CrawledItem
from readsetting import ReadSetting
from linkmatrix import LinkMatrix


class MatchSpider(CrawlSpider): #当url获取规则为“域名匹配及指定路径”
    name = "matchspider"

    def __init__(self):

        rs = ReadSetting()
        self.start_urls = rs.readurl()
        self.linkmatrix = LinkMatrix(rs.projectname())
        self.linkmatrix.setroot(self.start_urls)

        domains = rs.readdomain()
        self.allowed_domains = domains[0]

        self.rules = [Rule( LinkExtractor(allow = domains[1], deny = domains[2]),
            follow=True, callback="parse_domain")]

        super(MatchSpider, self).__init__()


    def parse_domain(self, response):
        self.log('receive response from {0}'.format(response.url), INFO)
        myitem = CrawledItem()
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

