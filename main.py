#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys, os
import time, logging

import scrapy
##from scrapy import cmdline, log, signals
from PyQt4 import QtCore, QtGui, uic
from addurl import addurl
from projectname import projectname
from setupspider import setupspider

from multiprocessing import Process, Pipe
##from GlobalLogging import GlobalLogging


class mycrawl(QtGui.QMainWindow):

    def __init__(self):
        super(mycrawl, self).__init__()
        ui_main = uic.loadUi("main.ui", self)
        self.logger = logging.getLogger("log")
        self.handler = logging.FileHandler("log.txt")
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        self.logger.info("\n\n----------------------------------------\n%s" \
                         %time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))
        self.logger.info("start")

        self.timer = QtCore.QTimer(self)


    def updateOutput(self): #将结果信息显示在界面
        s = []
        stoped = None
        while p_r_conn.poll(): #查询是否接收到结果信息
            a = p_r_conn.recv()
            s.append(a)
##        else:
##            print("pipe empty")
        if s:
            self.resultplainTextEdit.appendPlainText('\n'.join(s))

        if p_c_conn.poll(): #查询是否接收到控制信息
            c = p_c_conn.recv()
            if c == "stoped crawl":
                stoped = True
                self.spiderProcess.terminate()
                self.resultplainTextEdit.appendPlainText(u"\n-------finish--------\n")
                QtGui.QMessageBox.about(self, u"已完成", u"爬虫已完成")

        if not stoped:
            self.timer.singleShot(500, self.updateOutput) #500毫秒执行一次


    @QtCore.pyqtSlot()
    def on_newprojectaction_triggered(self): #新建一个scrapy项目
        self.logger.info("start new project")
        name = []
        self.projectname1 = projectname(name, self.logger)

        if (self.projectname1.exec_()):
            self.logger.info("the name of new project is: %s" %name)
        if name:
            self.name = name[0]
            self.projectnameLabel.setText(self.name)
        else:
            self.logger.info("new project is not started")


    @QtCore.pyqtSlot()
    def on_addurlButton_clicked(self): #添加起始url
        self.logger.info("add url")
        list_url = []
        self.addurl1 = addurl(list_url, self.logger)

        if (self.addurl1.exec_()):
            self.logger.info("the url list that user added is: %s" %list_url)
        if list_url:
            existed_url = str(self.urltextBrowser.toPlainText()).split('\n')
            existed_url = [e for e in existed_url if e is not ""]
            for e in list_url:
                if e not in existed_url:
                    existed_url.append(e)
            self.logger.info("the current url list is: %s" %existed_url)
            current_url = '\n'.join(existed_url)
            self.urltextBrowser.setText(current_url)

        self.logger.info("add url ending")


    @QtCore.pyqtSlot()
    def on_emptyurlButton_clicked(self): #清空起始url
        self.urltextBrowser.setText("")
        self.logger.info("empty the url")


    @QtCore.pyqtSlot()
    def on_savelocationpushButton_clicked(self): #选择文件保存的位置
        path = QtGui.QFileDialog.getExistingDirectory(self)
        s = unicode(path.toUtf8(), "utf8")
        self.savelocationlineEdit.setText(s)


    @QtCore.pyqtSlot()
    def on_autoacquireradioButton_clicked(self): #选择url获取规则为“从页面自动分析获取”
        self.logger.info("choose autospider")
        self.ruleplainTextEdit.setPlainText(u"不需要填写本编辑框")
        self.ruletextlabel.setText(u"不需要填写")
        self.rule = "auto"


    @QtCore.pyqtSlot()
    def on_matchradioButton_clicked(self): #选择url获取规则为“域名匹配及路径选择”
        self.logger.info("choose domainspider")
        self.ruleplainTextEdit.setPlainText(\
            "allowed_domains=('example.com')\nallow=('showstaff\.aspx', 'directory\.google\.com/[A-Z][a-zA-Z_/]+$')\ndeny=('shownodir\.aspx')")
        self.ruletextlabel.setText(u"按范例将引\n号中内容替\n换,三项均\n非必选项,\n一行一项")
        self.rule = "domain"


    @QtCore.pyqtSlot()
    def on_xpathradioButton_clicked(self): #选择url获取规则为“Xpath表达式”
        self.logger.info("choose xpathspider")
        self.ruleplainTextEdit.setPlainText(\
            "allowed_domains=('example.com')\nurl='//ul/li//div[2]/h2/a/@href'")
        self.ruletextlabel.setText(u"按范例将引\n号中内容替\n换,后一项\n为必选项,\n一行一项")
        self.rule = "xpath"


    @QtCore.pyqtSlot()
    def on_startButton_clicked(self): #开始爬取网页
        if self.projectnameLabel.text() == u"（未创建）": #判断是否创建了项目
            QtGui.QMessageBox.about(self, u"未创建项目", u"请新建一个项目，点击文件菜单新建项目")
        elif not self.urltextBrowser.toPlainText(): #判断是否已输入起始url
            QtGui.QMessageBox.about(self, u"未设置起始url", u"请设置起始url")
        elif not (self.autoacquireradioButton.isChecked() or self.matchradioButton.isChecked() \
                  or self.xpathradioButton.isChecked()): #判断是否已选择url获取规则
            QtGui.QMessageBox.about(self, u"未选择url获取规则", u"请选择url获取规则")
        elif not (self.savelocationlineEdit.text() and self.saveformatcomboBox.currentText() \
                  and self.namingcomboBox.currentText()): #判断是否已设置保存参数
            QtGui.QMessageBox.about(self, u"未设置保存参数", u"请设置保存参数")

        else:
            f = open("setting.txt", 'w')
            f.write("\n\nproject name: \n" + self.projectnameLabel.text())
            f.write("\n\ninitial url: \n" + self.urltextBrowser.toPlainText())
            f.write("\n\nrule: \n" + self.rule)
            if self.rule == "domain":
                f.write("\n\ndomain: \n" + self.ruleplainTextEdit.toPlainText())
            elif self.rule == "xpath":
                f.write("\n\nxpath: \n" + self.ruleplainTextEdit.toPlainText())
            f.write("\n\nlargest number of pages: \n" + str(self.pagenumberspinBox.value()))
            f.write("\n\nlargest number of items: \n" + str(self.itemnumberspinBox.value()))
            f.write("\n\ndepth of crawling: \n" + str(self.depthspinBox.value()))
            f.write("\n\nlongest time of requesting: \n" + str(self.requesttimespinBox.value()))
            f.write("\n\nlocation of saving: \n" + self.savelocationlineEdit.text().toUtf8())
            f.write("\n\nformat of saving: \n" + self.saveformatcomboBox.currentText())
            f.write("\n\nnaming of saving: \n" + self.namingcomboBox.currentText().toUtf8())
            f.close()
        self.logger.info("arguments of project have been saved in setting.txt")

        log_file = open("scrapy_log.txt", "w") #清空该txt文本以记录本次运行
        log_file.close()

        self.logger.info("start %s spider!" % self.rule)

        self.spiderProcess = Process(target = spiderProcess_entry, args=(c_s_conn, c_c_conn, c_r_conn)) #实例化spider进程,指向进程入口的函数
        self.spiderProcess.start()

        self.resultplainTextEdit.appendPlainText(u"-------start--------\n")
        QtGui.QMessageBox.about(self, u"开始", u"开始爬取")

        p_s_conn.send(self.rule)
        if(p_s_conn.recv() == "start crawl"):
            self.timer.singleShot(500, self.updateOutput)


    @QtCore.pyqtSlot()
    def closeEvent(self, event): #关闭界面,确保spider进程退出
        if self.spiderProcess.is_alive():
            self.spiderProcess.terminate()

def spiderProcess_entry(start_conn, contrl_conn, result_conn): #spider进程入口
    rule = start_conn.recv()
    start_conn.send("start crawl")

    the_spider = setupspider(rule, contrl_conn, result_conn) #实例化setupspider类
    the_spider.run()

if __name__ == "__main__":
    print("start")

    p_s_conn, c_s_conn = Pipe(True) #start connection, 实例化pipe
    p_r_conn, c_r_conn = Pipe() #result connection
    p_c_conn, c_c_conn = Pipe() #control connection

    app = QtGui.QApplication(sys.argv)
    win = mycrawl()
    win.show()

    app.exec_()

    sys.exit()

