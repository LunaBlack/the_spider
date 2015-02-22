

##class ExtensionThatAccessStats(object):
##    def __init__(self, stats):
##        self.stats = stats
##    @classmethod
##    def from_crawler(cls, crawler):
##        return cls(crawler.stats)


from scrapy import cmdline
cmdline.execute("scrapy crawl domainspider -o test_auto.json".split())







##from urllib import urlopen
##
##if __name__=='__main__':
##    url='http://www.baidu.com'
##    page=urlopen(url).read()
##    downpage=open('baidu.html','w')
##    downpage.write(page)
##    downpage.close()



##from twisted.internet import reactor
##from scrapy.crawler import Crawler
##from scrapy import log, signals
####from testspiders.spiders.followall import FollowAllSpider
##from scrapy.utils.project import get_project_settings
##from myproject.spiders.domain_spider import DomainSpider
##import myproject
##
##
##spider = DomainSpider()
##settings = myproject.settings
##crawler = Crawler(settings)
##crawler.signals.connect(reactor.stop, signal=signals.spider_closed)
##crawler.configure()
##crawler.crawl(spider)
##crawler.start()
##log.start()
##reactor.run()
