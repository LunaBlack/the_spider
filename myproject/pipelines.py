# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


import csv
import os
import urllib
import urllib2
import exceptions
import json
from scrapy.exceptions import DropItem
from readsetting import ReadSetting
from GlobalLogging import GlobalLogging



class DuplicatePipeline(object): #去除重复item

    def __init__(self):
        self.urls_seen = set() #设置一个队列，显示已经处理过的url

    def process_item(self, item, spider):
        if item['url'] in self.urls_seen:
            print ("Duplicate item found: %s" % item)
            raise DropItem("Duplicate item found: %s" % item)
        else:
            try:
                data = urllib.urlopen(item['url']).read()
            except exceptions.IOError:
                print ("Bad item found: %s" % item)
                raise DropItem("Bad item found: %s" % item)
            self.urls_seen.add(item['url'])
            return item


class CsvWriterPipeline(object): #把所有item写到csv文件里

    def __init__(self):
        self.f = open("item.csv", "w")
        self.f.close()

    def process_item(self, item, spider):
        self.f = open("item.csv", "a")
        self.f.write(item['idnumber'] + ',' + item['url'] + ',' + item['title'].encode("cp936") + '\n')
        self.f.close()
        GlobalLogging.getInstance().info("  crawled item[" + item['idnumber'] + "] " + item['title'] + " url:" + item['url'])
        return item


class FirstDownloadPipeline(object): #下载所有item对应的网页, 命名方式为"顺序数字"

    def __init__(self):
        rs = ReadSetting()
        self.location = rs.savinglocation()
        self.savingformat = rs.savingformat()
        self.success = 0 #成功下载页面数

    def process_item(self, item, spider):
        try:
            page = urllib.urlopen(item['url']).read()
            path = os.path.normcase("%s/%s.%s" % (self.location, item['idnumber'], self.savingformat))
            downpage = open(path, "w")
            downpage.write(page)
            downpage.close()
            self.success = self.success + 1
            GlobalLogging.getInstance().info("[success] downloaded " + item['title'] + " url:" + item['url'])
            GlobalLogging.getInstance().info("[stats] downloaditem :" + str(self.success))
        except:
            GlobalLogging.getInstance().error("[fail] downloaded " + item['title'] + " url:" + item['url'])
        return item


class SecondDownloadPipeline(object): #下载所有item对应的网页, 命名方式为"项目+顺序数字"

    def __init__(self):
        rs = ReadSetting()
        self.location = rs.savinglocation()
        self.savingformat = rs.savingformat()
        self.projectname = rs.projectname()
        self.success = 0 #成功下载页面数

    def process_item(self, item, spider):
        try:
            #print("process {0}".format(item['url']))
            #page = urllib.urlopen(item['url']).read()
            #print("processed")

            path = os.path.normcase("%s/%s.%s" % (self.location, (self.projectname + "+" + item['idnumber']), self.savingformat))
            #downpage = open(path, "w")
            #downpage.write(page)
            #downpage.close()
            with open(path, "w") as downpage:
                downpage.write(item['body'])

            self.success = self.success + 1
            GlobalLogging.getInstance().info("[success] downloaded " + item['title'] + " url:" + item['url'])
            GlobalLogging.getInstance().info("[stats] downloaditem :" + str(self.success))
        except:
            GlobalLogging.getInstance().error("[fail] downloaded " + item['title'] + " url:" + item['url'])

        return item


class ThirdDownloadPipeline(object): #下载所有item对应的网页, 命名方式为"Html:Title"

    def __init__(self):
        rs = ReadSetting()
        self.location = rs.savinglocation()
        self.savingformat = rs.savingformat()
        self.success = 0 #成功下载页面数

    def process_item(self, item, spider):
        try:
            number = 0
            filename = item['title']
            while True:
                path = os.path.normcase("%s/%s.%s" % (self.location, filename, self.savingformat))
                if os.path.exists(path):
                    number = number + 1
                    filename = item['title'] + "(" + str(number) + ")"
                    continue
                else:
                    page = urllib.urlopen(item['url']).read()
                    downpage = open(path, "w")
                    downpage.write(page)
                    downpage.close()
                    break
            self.success = self.success + 1
            GlobalLogging.getInstance().info("[success] downloaded " + item['title'] + " url:" + item['url'])
            GlobalLogging.getInstance().info("[stats] downloaditem :" + str(self.success))
        except:
            GlobalLogging.getInstance().error("[fail] downloaded " + item['title'] + " url:" + item['url'])
        return item




##class JsonWriterPipeline(object):
##
##    def __init__(self):
##        self.file = open('items.jl', 'wb')
##
##    def process_item(self, item, spider):
##        line = json.dumps(dict(item)) + '\n'
##        self.file.write(line)
##        return item


##class MyprojectPipeline(object):
##    def process_item(self, item, spider):
##        return item
