# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os, json, csv
from scrapy.exceptions import DropItem
from scrapy.log import INFO, DEBUG

from readsetting import ReadSetting
from GlobalLogging import GlobalLogging
from myproject.items import CrawledItem, PassItem


class SavePipeline(object): #下载符合抓取下载条件的网页

    def __init__(self):
        print('+SavePipeline')
        rs = ReadSetting() #读取setting文件中的保存参数
        self.savename = rs.savingname()
        self.location = rs.savinglocation()
        self.saveingformat = rs.savingformat()

        if self.savename == 1: #判断函数self.getpath对应的函数变量(相当于函数指针)
            self.getpath = self.getpath_1
        elif self.savename == 2:
            self.getpath = self.getpath_2
        elif self.savename == 3:
            self.getpath = self.getpath_3

        self.projectname = rs.projectname()

        try:
            os.mkdir(self.location) #创建下载内容所保存的文件夹(根据保存参数)
        except OSError as e:
            if e.errno == 17: pass


    #关于可变参数的说明: *args表示任何多个无名参数,为tuple即(); **kwargs表示关键字参数,为dict即{}
    #同时使用*args和**kwargs时,*args参数必须要列在**kwargs之前
    #此三个函数需要的参数数目不一致,为统一函数变量的形式而采用**kwargs

    #此三个函数返回标准化的路径名称:在不区分大小写的文件系统上,把路径转换为小写字母; 在Windows上,把正斜杠转换为反斜杠

    def getpath_1(self, **kwargs): #文件的命名方式为"顺序数字"
        return os.path.normcase(u"{0}/{1}.{2}".format(self.location, self.index, self.saveingformat))

    def getpath_2(self, **kwargs): #文件的命名方式为"项目+顺序数字"
        return os.path.normcase(u"{0}/{1}+{2}.{3}".format(self.location, self.projectname, self.index, self.saveingformat))

    def getpath_3(self, **kwargs): #文件的命名方式为"Html:Title"; 若重名,则在结尾添加"(数字)"以区分
        number = 0
        title = kwargs['title']
        path = os.path.normcase(u"{0}/{1}.{2}".format(self.location, title, self.saveingformat))
        while os.path.exists(path): #若重名,则在结尾添加"(数字)"以区分
            number += 1
            filename = u"{0} ({1})".format(title, number)
            path = os.path.normcase(u"{0}/{1}.{2}".format(self.location, filename, self.saveingformat))
        return path

    def open_spider(self, spider): #启动spider进程时,自动调用该函数,初始化页面计数器
        print("+SavePipeline opened spider")
        self.index = 0 #记录符合下载条件的页面数
        self.page_count = dict() #符合下载条件的页面及其对应编号的字典对象
        self.success = 0 #记录成功下载的条目数

    def close_spider(self, spider): #结束spider时,自动调用该函数,传递符合下载条件的页面及其对应编号的字典对象
        spider.linkmatrix.setIndexMap(self.page_count)

    def process_item(self, item, spider): #下载保存(抓取下载范围内的)页面
        try: #try部分: 报错前的程序不回滚,即前两个计数器始终执行+1; 报错后的程序不执行
            self.index += 1
            #item['url'] = item['url'].strip('/')
            self.page_count.setdefault(item['url'].strip('/'), self.index)
            GlobalLogging.getInstance().info("[stats] scrapeditem : {0}".format(self.index))

            with open(self.getpath(title = item['title']), "w") as downpage:
                downpage.write(item['body'])

            self.success += 1

            spider.log('downloaded item from {0}'.format(item['url']), INFO)
            GlobalLogging.getInstance().info(u"[success] downloaded {0}\n         url: {1}".format(item['title'], item['url']))
            GlobalLogging.getInstance().info("[stats] downloaditem : {0}".format(self.success))
        except IOError as e:
            GlobalLogging.getInstance().info(u"[fail] download, {1}: {2}\n         url: {0}".format(item['url'], e.strerror, e.filename))

        return item


class StatisticsPipeline(object): #对爬取到的页面进行分类统计

    def __init__(self):
        print('+StatisticsPipeline')
        rs = ReadSetting() #读取setting文件中的保存参数
        self.pagecount_max = rs.pagenumber() #读取“最大爬取页面数”
        self.itemcount_max = rs.itemnumber() #读取“最大抓取条目数”
        self.pagecount = 0 #设置“爬取页面数”的计数器
        self.itemcount = 0 #设置“抓取下载条目数”的计数器
        self.page_seen = set() #初始化爬取页面列表
        self.item_seen = set() #初始化抓取下载条目列表

    def process_item(self, item, spider): #对爬取到的页面进行分类统计,其中的CrawledItem传给SavePipeline类进行下载

        if isinstance(item, PassItem): #若页面是PassItem
            if self.pagecount == self.pagecount_max: #若爬取页面数达到最大值
                GlobalLogging.getInstance().info("[stop_pagecount] reach max pagecount : {0}".format(self.pagecount)) #发消息停止spider
                self.pagecount += 1 #使self.pagecount > self.pagecount_max,之后不再接收新的PassItem
                raise DropItem("PassItem: %s" % item['url']) #丢弃该item
            elif self.pagecount > self.pagecount_max or self.itemcount >= self.itemcount_max: #若爬取页面数或抓取下载条目数超过最大值
                raise DropItem("PassItem: %s" % item['url'])

            url = item['url']
            if 'bcat2010062966' in url and  'tcat2010060846' in url:
                spider.log('downloaded item from {0}'.format(item['url']), INFO)
            spider.linkmatrix.addentirelink(item['url'], item['referer']) #记录到entire_struct字典对象中

            url = item['url'].strip('/')
            if url not in self.page_seen: #判断item是否重复
                self.page_seen.add(url)
                self.pagecount += 1 #爬取页面数加1

            raise DropItem("PassItem: %s" % item['url']) #丢弃该item

        elif isinstance(item, CrawledItem): #若页面是CrawledItem
            if self.itemcount == self.itemcount_max: #若抓取下载条目数达到最大值
                GlobalLogging.getInstance().info("[stop_itemcount] reach max itemcount : {0}".format(self.itemcount)) #发消息停止spider
                self.itemcount += 1 #使self.itemcount > self.itemcount_max,之后不再接收新的CrawledItem
                raise DropItem("Duplicate item found: %s" % item['url']) #丢弃该item
            elif self.itemcount > self.itemcount_max or self.pagecount >= self.pagecount_max: #若抓取下载条目数或爬取页面数超过最大值
                raise DropItem("Duplicate item found: %s" % item['url'])

            spider.linkmatrix.addforwardlink(item['url'], item['referer']) #记录到forwardlinks字典对象中

            url = item['url'].strip('/')
            if url not in self.item_seen: #判断item是否重复
                self.item_seen.add(url)
                self.itemcount += 1 #爬取下载条目数加1
                return item
            else:
                raise DropItem("Duplicate item found: %s" % item['url']) #丢弃该item

