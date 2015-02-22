# -*- coding: utf-8 -*-


from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from myproject.spiders.domain_spider import DomainSpider #项目中spider目录下可用的spider类
from scrapy.utils.project import get_project_settings
from multiprocessing import Process


def setup_crawler():
    print "start"
    spider = DomainSpider()   #创建一个爬虫实例
    settings = get_project_settings()
    crawler = Crawler(settings)
    crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
    crawler.configure()
    crawler.crawl(spider)
    f = open("scrapy_log.txt", "w")
    log.start(logfile = "scrapy_log.txt", loglevel = "DEBUG")
    crawler.start()
    reactor.run()
##    f.close()
##    print "close"
##    reactor.stop()
##    print "stop"




##if __name__ == "__main__":
##    setup_crawler()
##    log.start()
##    reactor.run()

##a = setup_crawler()

if __name__ == "__main__":
    p = Process(target = setup_crawler)
    p.start()
    p.join()
    print "end"


##log.start()
##reactor.run()
##crawler.signals.connect(reactor.stop, signal=signals.spider_closed)

##a.addBoth(lambda _: reactor.stop())



##class UrlCrawlerScript(Process):
##        def __init__(self, spider):
##            Process.__init__(self)
##            settings = get_project_settings()
##            self.crawler = Crawler(settings)
##
##            if not hasattr(project, 'crawler'):
##                self.crawler.install()
##                self.crawler.configure()
##                self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
##            self.spider = spider
##
##        def run(self):
##            self.crawler.crawl(self.spider)
##            self.crawler.start()
##            reactor.run()
##
##def run_spider(url):
##    spider = MySpider(url)
##    crawler = UrlCrawlerScript(spider)
##    crawler.start()
##    crawler.join()





##from scrapy.crawler import Crawler
##from scrapy.conf import settings
##from myproject.spiders.domain_spider import DomainSpider
##from scrapy import log, project
##from twisted.internet import reactor
##from billiard import Process
##from scrapy.utils.project import get_project_settings
##
##class UrlCrawlerScript(Process):
##        def __init__(self, spider):
##            Process.__init__(self)
##            settings = get_project_settings()
##            self.crawler = Crawler(settings)
##
##            if not hasattr(project, 'crawler'):
##                self.crawler.install()
##                self.crawler.configure()
##                self.crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
##            self.spider = spider
##
##        def run(self):
##            self.crawler.crawl(self.spider)
##            self.crawler.start()
##            reactor.run()
##
##def run_spider():
##    spider = DomainSpider()
##    crawler = UrlCrawlerScript(spider)
##    crawler.start()
##    crawler.join()
