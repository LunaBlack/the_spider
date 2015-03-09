# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import os
import json
import csv
from scrapy.exceptions import DropItem
from readsetting import ReadSetting
from GlobalLogging import GlobalLogging


class SavePipeline(object): #下载所有item对应的网页

    def __init__(self):
        print('+SavePipeline')
        rs = ReadSetting()
        self.savename = rs.savingname()
        self.location = rs.savinglocation()
        self.saveingformat = rs.savingformat()

        if self.savename == 1:
            self.getpath = self.getpath_1
        elif self.savename == 2:
            self.getpath = self.getpath_2
        elif self.savename == 3:
            self.getpath = self.getpath_3

        self.projectname = rs.projectname()

        try:
            os.mkdir(self.location)
        except OSError as e:
            if e.errno == 17: pass

    def getpath_1(self, **kwargs):
        return os.path.normcase(u"{0}/{1}.{2}".format(self.location, self.index, self.saveingformat))

    def getpath_2(self, **kwargs):
        return os.path.normcase(u"{0}/{1}+{2}.{3}".format(self.location, self.projectname, self.index, self.saveingformat))

    def getpath_3(self, **kwargs):
        number = 0
        title = kwargs['title']
        path = os.path.normcase(u"{0}/{1}.{2}".format(self.location, title, self.saveingformat))
        while os.path.exists(path):
            number += 1
            filename = u"{0} ({0})".format(title, number)
            path = os.path.normcase(u"{0}/{1}.{2}".format(self.location, filename, self.saveingformat))
        return path

    def open_spider(self, spider):
        print("+SavePipeline opened spider")
        self.index = 0 #成功下载页面数
        self.page_count = dict()

    def close_spider(self, spider):
        spider.linkmatrix.setIndexMap(self.page_count)

    def process_item(self, item, spider):
        try:
            self.index += 1
            self.page_count.setdefault(item['url'], self.index)

            with open(self.getpath(title = item['title']), "w") as downpage:
                downpage.write(item['body'])

            GlobalLogging.getInstance().info(u"[success] downloaded {0}\n         url: {1}".format(item['title'], item['url']))
            GlobalLogging.getInstance().info("[stats] downloaditem : {0}".format(self.index))
        except KeyError:
            GlobalLogging.getInstance().error(u"[fail] download\n         url: {0}".format(item['url']))
        except IOError as e:
            GlobalLogging.getInstance().error(u"[fail] download, {1}: {2}\n         url: {1}".format(item['url'], e.strerror, e.filename))

        return item


class StatisticsPipeline(object):

    def __init__(self):
        print('+StatisticsPipeline')

    def process_item(self, item, spider):

        if spider.linkmatrix.addLink(item['url'], item['referer']):
            #print ("Duplicate item found: %s" % item)
            raise DropItem("Duplicate item found: %s" % item)
        else:
            return item

