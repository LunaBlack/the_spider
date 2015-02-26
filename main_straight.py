#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys
import time, logging
from multiprocessing import Process, Pipe

from PyQt4 import QtCore, QtGui, uic
from addurl import addurl
from projectname import projectname
from setupspider import setupspider

##from GlobalLogging import GlobalLogging
from linkmatrix import LinkMatrix


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
        self.timer.timeout.connect(self.updateOutput)


    def updateOutput(self): #将结果信息显示在界面
        s = list()
        stoped = None

        while self.result_conn[0].poll(): #查询是否接收到结果信息
            a = self.result_conn[0].recv()
            s.append(a)

        if s:
            self.resultplainTextEdit.appendPlainText('\n'.join(s))

        while self.state_conn[0].poll(): #查询是否接收到状态信息
            a = self.state_conn[0].recv()
            if "downloader/request_count:" in a:
                self.requestcountLabel.setText(a[64:].strip()) #改变请求页面数
            elif "downloader/response_count:" in a:
                self.responsecountLabel.setText(a[65:].strip()) #改变响应页面数
            elif "downloader/response_bytes:" in a:
                self.responsebytesLabel.setText(a[65:].strip()) #改变响应字节数
            elif "downloader/response_status_count/200:" in a:
                self.response200countLabel.setText(a[76:].strip()) #改变成功响应页面数(200)
            elif "item_scraped_count:" in a:
                self.itemscrapedLabel.setText(a[58:].strip()) #改变抓取条目数
            elif "downloaditem :" in a:
                self.itemdownloadLabel.setText(a[27:].strip()) #改变成功下载条目数

        if self.ctrl_conn[0].poll(): #查询是否接收到控制信息
            c = self.ctrl_conn[0].recv()
            if c == "stoped crawl":
                stoped = True
                self.spiderProcess.terminate()
                self.resultplainTextEdit.appendPlainText(u"\n-------finish--------\n")
                self.statusLabel.setText(u"已完成") #改变运行状态Label
                QtGui.QMessageBox.about(self, u"已完成", u"爬虫已完成")

        if stoped:
            #self.timer.singleShot(500, self.updateOutput) #500毫秒执行一次
            self.timer.stop()


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


    def check_ready(self):
        if self.projectnameLabel.text() == u"（未创建）": #判断是否创建了项目
            QtGui.QMessageBox.about(self, u"未创建项目", u"请新建一个项目，点击文件菜单新建项目")
            return False
        elif not self.urltextBrowser.toPlainText(): #判断是否已输入起始url
            QtGui.QMessageBox.about(self, u"未设置起始url", u"请设置起始url")
            return False
        elif not (self.autoacquireradioButton.isChecked() or self.matchradioButton.isChecked() \
                  or self.xpathradioButton.isChecked()): #判断是否已选择url获取规则
            QtGui.QMessageBox.about(self, u"未选择url获取规则", u"请选择url获取规则")
            return False
        elif not (self.savelocationlineEdit.text() and self.saveformatcomboBox.currentText() \
                  and self.namingcomboBox.currentText()): #判断是否已设置保存参数
            QtGui.QMessageBox.about(self, u"未设置保存参数", u"请设置保存参数")
            return False
        else:
            return True


    def write_setting(self):
        with open("setting.txt", 'w') as f:
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


    @QtCore.pyqtSlot()
    def on_startButton_clicked(self): #开始爬取网页
        self.rule = "domain"

        #self.logger.info("arguments of project have been saved in setting.txt")

        log_file = open("scrapy_log.txt", "w") #清空该txt文本以记录本次运行
        log_file.close()

        #self.logger.info("start %s spider!" % self.rule)

        self.main_conn = Pipe(True) #start connection, 实例化pipe
        self.result_conn = Pipe() #result connection
        self.ctrl_conn = Pipe() #control connection
        self.state_conn = Pipe() #state connection

        self.spiderProcess = Process(target = spiderProcess_entry, args=(self.main_conn[1], self.ctrl_conn[1], self.result_conn[1], self.state_conn[1]))
        self.spiderProcess.start()

        self.tabWidget.setCurrentIndex(1)
        self.running = True
        self.statusLabel.setText(u"正在运行") #改变运行状态Label
        self.resultplainTextEdit.appendPlainText(u"-------start--------\n")

        self.main_conn[0].send(self.rule)
        if self.main_conn[0].recv() == "start crawl":
            #self.timer.singleShot(500, self.updateOutput)
            self.timer.start(500)


    @QtCore.pyqtSlot()
    def on_pauseButton_clicked(self):
        if self.running:
            self.running = not self.running
            self.pauseButton.setText(u"恢复")
            self.statusLabel.setText(u"暂停") #改变运行状态Label
            self.ctrl_conn[0].send('pause crawl')
        else:
            self.running = not self.running
            self.pauseButton.setText(u"暂停")
            self.statusLabel.setText(u"正在运行") #改变运行状态Label
            self.ctrl_conn[0].send('unpause crawl')

    @QtCore.pyqtSlot()
    def on_stopButton_clicked(self):
        self.ctrl_conn[0].send('stop crawl')

    @QtCore.pyqtSlot()
    def closeEvent(self, event): #关闭界面,确保spider进程退出
        if self.timer.isActive():
            self.timer.stop()

        try:
            if self.spiderProcess.is_alive():
                self.spiderProcess.terminate()
                time.sleep(3)
                if self.spiderProcess.is_alive():
                    print("""
===========================send signal 9==================================""")
                    self.spiderProcess.send_signal(9)
        except AttributeError:
            pass

    @QtCore.pyqtSlot()
    def on_exportaction_2_triggered(self):
        lm = LinkMatrix()
        lm.load()
        matrix = lm.export_matrix()

def spiderProcess_entry(main_conn, contrl_conn, result_conn, state_conn): #spider进程入口
    rule = main_conn.recv()
    main_conn.send("start crawl")

    the_spider = setupspider(rule, contrl_conn, result_conn, state_conn) #实例化setupspider类
    the_spider.run()

if __name__ == "__main__":
    print("start")

    app = QtGui.QApplication(sys.argv)
    win = mycrawl()
    win.show()

    app.exec_()

    sys.exit()
    print("exit")

