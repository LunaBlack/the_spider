from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings
from myproject.spiders.domain_spider import DomainSpider


class ReactorControl:

    def __init__(self):
        self.crawlers_running = 0

    def add_crawler(self):
        self.crawlers_running += 1

    def remove_crawler(self):
        self.crawlers_running -= 1
        if self.crawlers_running == 0 :
            reactor.stop()

def setup_crawler(spider_name):
    crawler = Crawler(settings)
    crawler.configure()
    crawler.signals.connect(reactor_control.remove_crawler, signal=signals.spider_closed)
    spider = DomainSpider()
    crawler.crawl(spider)
    reactor_control.add_crawler()
    crawler.start()

reactor_control = ReactorControl()
f = open("scrapy_log.txt", "w")
log.start(logfile = "scrapy_log.txt", loglevel = "DEBUG")
settings = get_project_settings()
crawler = Crawler(settings)

for spider_name in crawler.spiders.list():
    setup_crawler(DomainSpider)

print "start"
reactor.run()
print "stop"
