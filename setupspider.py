# -*- coding: utf-8 -*-

import time, logging, sys

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings

from myproject.spiders.auto_spider import AutoSpider #此三行导入项目中spider目录下可用的spider类
from myproject.spiders.domain_spider import DomainSpider
from myproject.spiders.xpath_spider import XpathSpider

#import myproject.spiders.auto_spider
#import myproject.spiders.domain_spider
#import myproject.spiders.xpath_spider

from GlobalLogging import GlobalLogging


class setupspider():
    def __init__(self, rule, contrl_conn, result_conn, stats_conn):
        self.rule = rule
        self.ctrl_conn = contrl_conn
        self.result_conn = result_conn
        self.stats_conn = stats_conn

        self.settings = get_project_settings()
        self.crawler = Crawler(self.settings)
        self.crawler.configure()

        self.crawler.signals.connect(self.stop, signal = signals.spider_closed)

        self.spider = None

        GlobalLogging.getInstance().setLoggingToHanlder(self.getLog)
        GlobalLogging.getInstance().setLoggingLevel(logging.INFO)


    def getLog(self, s): #将结果信息传给主进程
        #print(s)
        if s.startswith("INFO"):
            log_type = s[s.index('[')+1 : s.index(']')]
            if log_type == "success":
                self.result_conn.send(s)
            elif log_type == "fail":
                self.result_conn.send(s)
            elif log_type == "stats":
                self.stats_conn.send(s)
                pass
        else:
            print(s)

        if self.ctrl_conn.poll(): #查询是否接收到控制信息
            c = self.ctrl_conn.recv()
            if c == 'stop crawl':
#                print("""
#=============================received stop==================================""")
                self.crawler.stop()
            elif c == 'pause crawl':
                self.crawler.engine.pause()
            elif c == 'unpause crawl':
                self.crawler.engine.unpause()


    def run(self):
        log.start(logfile = "scrapy_log.txt", loglevel = "INFO", logstdout = False)

        if self.rule == "auto":
            self.spider = AutoSpider()   #创建一个auto_spider的爬虫实例
        elif self.rule == "domain":
            self.spider = DomainSpider()   #创建一个domain_spider的爬虫实例
        elif self.rule == "xpath":
            self.spider = XpathSpider()   #创建一个xpath_spider的爬虫实例

        if self.spider:
            self.crawler.crawl(self.spider)
            self.crawler.start()
            reactor.run()


    def stop(self):
        self.spider.linkmatrix.store()
        if reactor.running:
            reactor.stop()
        self.ctrl_conn.send("stoped crawl") #将控制信息"停止"传给主进程

