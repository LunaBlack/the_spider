# encoding: utf-8


import re

from scrapy import signals
from scrapy.http import Request
from scrapy.utils.httpobj import urlparse_cached
from scrapy import log

class OffsiteMiddleware(object): #中间件,过滤掉爬取范围(限定域)外的链接

    def __init__(self, stats):
        self.stats = stats

    @classmethod
    def from_crawler(cls, crawler):
        o = cls(crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        return o

    def process_spider_output(self, response, result, spider):
        for x in result: #result为item或者request,从spider接收
            if isinstance(x, Request): #若x为Request
                if x.dont_filter or self.should_follow(x, spider): #x请求的url在爬取范围(限定域)内,且不需过滤
                    domain = urlparse_cached(x).hostname #解析出x(即Request(url))中的url所对应的domain(实际上为url的host)
                    log.msg(format="Pass request to %(domain)r: %(request)s (%(donot)s)", 
                            level=log.DEBUG, spider=spider, domain=domain, request=x, donot=x.dont_filter) #写一行log,说明放行此Request
                    yield x
                else:
                    domain = urlparse_cached(x).hostname #解析出domain(实际上为url的host)
                    if domain and domain not in self.domains_seen: #若domain(实际上为url的host)存在,且domain(实际上为url的host)第一次出现
                        self.domains_seen.add(domain) #添加到已知domain(已知domain(即domains_seen队列)内不包含allowed_domains)
                        self.stats.inc_value('offsite/domains', spider=spider) #调整状态收集器中对应的值,计数器(统计限定域外的域)加1
                        log.msg(format="Filtered offsite request to %(domain)r: %(request)s",
                                level=log.DEBUG, spider=spider, domain=domain, request=x) #写一行log,说明过滤掉一个爬取范围(限定域)外的Request
                    spider.linkmatrix.addoutlink(x.url, x.headers['Referer']) #将url添加到外链表中,x.url为请求的url,referer为指向这个url页面的url(即链接起点端)
                    self.stats.inc_value('offsite/filtered', spider=spider) #调整状态收集器中对应的值,计数器(统计过滤掉的Request)加1
            else: #若x为item
                yield x

    def should_follow(self, request, spider): #判断request请求的url是否在爬取范围(限定域)内,若在爬取范围(限定域)内则返回True
        regex = self.host_regex #regex是一个编译过的正则表达式,这个正则表达式匹配的是spider的allowd_domains属性中含有的domain
        # hostname can be None for wrong urls (like javascript links)
        host = urlparse_cached(request).hostname or '' #解析出request请求的url所对应的host
        return bool(regex.search(host)) #判断解析出的host是否在allowed_domains范围内

    def get_host_regex(self, spider): #返回一个匹配spider.allowed_domains中所有domain的正则表达式
        """Override this method to implement a different offsite policy"""
        allowed_domains = getattr(spider, 'allowed_domains', None) #获取spider.allowed_domains的值; 若spider未设置allowed_domains属性,则返回None
        if not allowed_domains: #若spider未设置allowed_domains属性
            return re.compile('') # allow all by default
        regex = r'^(.*\.)?(%s)$' % '|'.join(re.escape(d) for d in allowed_domains if d is not None) #生成正则表达式
        #log.msg(format="Filter regex: %(regex)s", level=log.DEBUG, regex=regex)
        return re.compile(regex)

    def spider_opened(self, spider): #spider开启时,自动被调用
        self.host_regex = self.get_host_regex(spider) #获取一个匹配spider.allowed_domains中所有domain的正则表达式
        self.domains_seen = set() #初始化已知domain

