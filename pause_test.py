# -*- coding: utf-8 -*-

from scrapy import cmdline
import time
##cmdline.execute("scrapy crawl domainspider".split())


time.sleep(3)
cmdline.execute("scrapy crawl domainspider -s JOBDIR=crawls/domainspider-1".split())


##time.sleep(3)
##cmdline.execute("scrapy crawl domainspider -s JOBDIR=crawls/domainspider-1".split())


##from twisted.internet import reactor
##from scrapy.crawler import Crawler
##from scrapy import log, signals
##from myproject.spiders.domain_spider import DomainSpider #项目中spider目录下可用的spider类
##from scrapy.utils.project import get_project_settings
##
##def setup_crawler():
##    spider = DomainSpider()   #创建一个爬虫实例
##    settings = get_project_settings()
##    crawler = Crawler(settings)
##    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
##    crawler.configure()
##    crawler.crawl(spider)
##    crawler.start()
##    log.start()
##    reactor.run()
##    
##
##
####if __name__ == "__main__":
####    setup_crawler()
####    log.start()
####    reactor.run()
##
####a = setup_crawler()
##setup_crawler()
