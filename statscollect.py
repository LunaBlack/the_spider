#!/usr/bin/python
#-*-coding:utf-8-*-


from scrapy import log
from socket import socket
from time import time
from scrapy.statscol import StatsCollector
from GlobalLogging import GlobalLogging


STATS_KEY = 'scrapy:stats'


class SpiderStatsCollector(StatsCollector):

    SPIDER_IGNOREKEYS = []#to ignore it, prevent to send data to GlobaoLogging
    
    def __init__(self, crawler):
        super(SpiderStatsCollector, self).__init__(crawler)
        self.ignore_keys = crawler.settings.get("SPIDER_IGNOREKEYS", self.SPIDER_IGNOREKEYS)


    def _get_stats_key(self, spider, key):
        if spider is not None:
            return "scrapy.spider.%s.%s" % (spider.name, key)
        return "scrapy.%s" % (key)


    def set_value(self, key, value, spider=None):
        super(SpiderStatsCollector, self).set_value(key, value, spider)
        self._set_value(key, value, spider)


    def _set_value(self, key, value, spider):
        if isinstance(value, (int, float)) and key not in self.ignore_keys:
            k = self._get_stats_key(spider, key)
            GlobalLogging.getInstance().info("[stats]" + k + ":" + value)


    def inc_value(self, key, count=1, start=0, spider=None):
        super(SpiderStatsCollector, self).inc_value(key, count, start, spider)
        GlobalLogging.getInstance().info("[stats]" + self._get_stats_key(spider, key) + ":" + str(self.get_value(key)))


    def max_value(self, key, value, spider=None):
        super(SpiderStatsCollector, self).max_value(key, value, spider)
        GlobalLogging.getInstance().info("[stats]" + self._get_stats_key(spider, key) + ":" + str(self.get_value(key)))


    def min_value(self, key, value, spider=None):
        super(SpiderStatsCollector, self).min_value(key, value, spider)
        GlobalLogging.getInstance().info("[stats]" + self._get_stats_key(spider, key) + ":" + str(self.get_value(key)))


    def set_stats(self, stats, spider=None):
        super(SpiderStatsCollector, self).set_stats(stats, spider)
        for key in stats:
            self._set_value(key, stats[key], spider)
