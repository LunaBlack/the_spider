# -*- coding: utf-8 -*-

import time, logging, sys

from twisted.internet import reactor
from scrapy.crawler import Crawler
from scrapy import log, signals
from scrapy.utils.project import get_project_settings

from myproject.spiders.auto_spider import AutoSpider #此四行导入项目中spider目录下可用的spider类
from myproject.spiders.match_spider import MatchSpider
from myproject.spiders.xpath_spider import XpathSpider
from myproject.spiders.xpath_spider0 import XpathSpider0

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

        self.crawler.signals.connect(self.stop, signal = signals.spider_closed) #当spider终止时,自动调用stop函数

        self.spider = None

        GlobalLogging.getInstance().setLoggingToHanlder(self.getLog) #初始化GlobalLogging的设置
        GlobalLogging.getInstance().setLoggingLevel(logging.INFO)


    def getLog(self, s): #将结果信息传给主进程
        if s.startswith("INFO"):
            log_type = s[s.index('[')+1 : s.index(']')]
            if log_type == "success":
                self.result_conn.send(s)
            elif log_type == "fail":
                self.result_conn.send(s)
            elif log_type == "stats":
                self.stats_conn.send(s)
            elif log_type =="stop_pagecount":
                self.crawler.stop()
            elif log_type =="stop_itemcount":
                self.crawler.stop()
        else:
            pass

        if self.ctrl_conn.poll(): #查询是否接收到控制信息
            c = self.ctrl_conn.recv()
            if c == 'stop crawl':
                self.crawler.stop()
            elif c == 'pause crawl':
                self.crawler.engine.pause()
                while 1:
                    if self.ctrl_conn.poll(1):
                        c = self.ctrl_conn.recv()
                        if c == 'unpause crawl':
                            self.crawler.engine.unpause()
                            break
                        elif c == 'stop crawl':
                            self.crawler.stop()
                            break


    def run(self):
        log.start(logfile = "scrapy_log.txt", loglevel = "INFO", logstdout = False)

        if self.rule == "auto":
            self.spider = AutoSpider()   #创建一个auto_spider的爬虫实例
        elif self.rule == "match":
            self.spider = MatchSpider()   #创建一个match_spider的爬虫实例
        elif self.rule == "xpath":
            self.spider = XpathSpider()   #创建一个xpath_spider的爬虫实例
        elif self.rule == "xpath0":
            self.spider = XpathSpider0()   #创建一个xpath_spider0的爬虫实例

        if self.spider:
            self.crawler.crawl(self.spider)
            self.crawler.start()
            reactor.run()


    def stop(self):
        if reactor.running:
            reactor.stop()

        self.spider.linkmatrix.structure_entirelink() #构建entire_struct字典对象
        self.spider.linkmatrix.structure_forwardlinks() #构建forwardlinks字典对象
        self.spider.linkmatrix.structure_outlinks() #构建outlinks字典对象
        self.spider.linkmatrix.store() #以数据流形式将字典对象写入文件
        self.ctrl_conn.send("stoped crawl") #将控制信息"停止"传给主进程

