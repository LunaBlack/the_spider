# -*- coding: utf-8 -*-

# Scrapy settings for myproject project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#


from readsetting import ReadSetting

print("import setting.py")
rs = ReadSetting()


BOT_NAME = 'myproject'

SPIDER_MODULES = ['myproject.spiders']
NEWSPIDER_MODULE = 'myproject.spiders'


DEPTH_LIMIT = rs.depth() #限制爬取深度

DOWNLOAD_TIMEOUT = rs.requesttime() #下载器超时时间(单位:秒)

CLOSESPIDER_PAGECOUNT = rs.pagenumber() #指定最大的抓取响应(reponses)数

CLOSESPIDER_ITEMCOUNT = rs.itemnumber() #指定条目的个数


CONCURRENT_REQUESTS = 50 #Scrapy downloader并发请求(concurrent requests)的最大值

CONCURRENT_ITEMS = 100 #Item Processor(即Item Pipeline)同时处理(每个response的)item的最大值

DUPEFILTER_DEBUG = True #记录所有重复的requests

COOKIES_ENABLED = False #禁止cookies

AJAXCRAWL_ENABLED = True #启用“Ajax Crawlable Pages”爬取

STATS_CLASS = 'statscollect.SpiderStatsCollector' #设置状态收集器


ITEM_PIPELINES = {
        'myproject.pipelines.StatisticsPipeline': 300,
        'myproject.pipelines.SavePipeline': 500, }



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'myproject (+http://www.yourdomain.com)'
