#!/usr/bin/python2
# -*- coding: utf-8 -*-

import sys, os
import time, logging
from multiprocessing import Process, Pipe
import platform
if platform.system() == 'Windows':
    import win32com.client, win32api

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
        self.request_count = '0'
        self.response_count = '0'
        self.response_bytes = '0'
        self.response_200_count = '0'
        self.item_scraped_count = '0'
        self.downloaditem_count = '0'

    def updateOutput(self): #将结果信息显示在界面
        self.runningtime += self.running and 0.5 or 0
        hour = int(self.runningtime)//3600
        minute = int(self.runningtime - hour*3600) // 60
        second = int(self.runningtime) % 60
        self.runtimeLabel.setText("{0:02}:{1:02}:{2:02}".format(hour, minute, second))

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
                self.request_count = a[64:].strip()
                self.requestcountLabel.setText(self.request_count) #改变请求页面数
            elif "downloader/response_count:" in a:
                self.response_count = a[65:].strip()
                self.responsecountLabel.setText(self.response_count) #改变响应页面数
            elif "downloader/response_bytes:" in a:
                self.response_bytes = a[65:].strip()
                self.responsebytesLabel.setText(self.response_bytes) #改变响应字节数
            elif "downloader/response_status_count/200:" in a:
                self.response_200_count = a[76:].strip()
                self.response200countLabel.setText(self.response_200_count) #改变成功响应页面数(200)
            elif "item_scraped_count:" in a:
                self.item_scraped_count = a[58:].strip()
                self.itemscrapedLabel.setText(self.item_scraped_count) #改变抓取条目数
            elif "downloaditem :" in a:
                self.downloaditem_count = a[27:].strip()
                self.itemdownloadLabel.setText(self.downloaditem_count) #改变成功下载条目数

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
            self.running = False
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
        self.rule = "xpath"

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
        self.statusLabel.setText(u"正在运行") #改变运行状态Label
        self.resultplainTextEdit.appendPlainText(u"-------start--------\n")
        #QtGui.QMessageBox.about(self, u"开始", u"开始爬取")

        self.main_conn[0].send(self.rule)
        if self.main_conn[0].recv() == "start crawl":
            #self.timer.singleShot(500, self.updateOutput)
            self.running = True
            self.runningtime = 0
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

    def write_final_stats(self):
        with open(unicode("wlv", 'utf8')+'/final stats.txt', 'w') as f:
            lines = []
            lines.append("downloader/request_count: {0}\n".format(self.request_count) )
            lines.append("downloader/response_count: {0}\n".format(self.response_count) )
            lines.append("downloader/response_bytes: {0}\n".format(self.response_bytes) )
            lines.append("downloader/response_status_count/200: {0}\n".format(self.response_200_count) )
            lines.append("item_scraped_count: {0}\n".format(self.item_scraped_count) )
            lines.append("downloaditem : {0}\n".format(self.downloaditem_count) )
            f.writelines(lines)

    @QtCore.pyqtSlot()
    def on_startprojectaction_triggered(self): #通过菜单开始爬取
        self.on_startButton_clicked()

    @QtCore.pyqtSlot()
    def on_pauseprojectaction_triggered(self): #通过菜单暂停爬取
        self.on_pauseButton_clicked()

    @QtCore.pyqtSlot()
    def on_stopprojectaction_triggered(self): #通过菜单停止爬取
        self.on_stopButton_clicked()

    @QtCore.pyqtSlot()
    def on_exitsoftwareaction_triggered(self): #通过菜单退出软件
        self.closeEvent(event)

    @QtCore.pyqtSlot()
    def on_buildoutputaction_triggered(self):
        lm = LinkMatrix("wlv")
        lm.load()
        #lm.export_matrix(self.projectnameLabel.text())
        lm.export_matrix()
        self.write_final_stats()
        QtGui.QMessageBox.about(self, u"已保存", u"已保存")

    @QtCore.pyqtSlot()
    def on_action1_triggered(self): #打开"运行结果"文件
        f = self.name + "final stats.txt"
        f_path = os.path.abspath(f_path)
        if os.path.exists(f_path):
            try:
                if platform.system() == 'Windows':
                    win32api.ShellExecute(0, 'open', 'notepad.exe', f_path, '', 1)
                elif platform.system() == 'Linux':
                    os.system('xdg-open {0}'.format(f_path))
            except:
                QtGui.QMessageBox.about(self, u"无法打开文件", u"无法打开文件")
        else:
            QtGui.QMessageBox.about(self, u"文件不存在", u"文件不存在")

    def opentxtfile(self, f_path): #打开txt格式文件
        if os.path.exists(f_path):
            try:
                if platform.system() == 'Windows':
                    win32api.ShellExecute(0, 'open', 'notepad.exe', f_path, '', 1)
                else:
                    os.system('xdg-open {0}'.format(f_path))
            except:
                QtGui.QMessageBox.about(self, u"无法打开文件", u"无法打开文件")
        else:
            QtGui.QMessageBox.about(self, u"请先生成统计结果", u"请先生成统计结果,点击分析菜单完成")

    @QtCore.pyqtSlot()
    def on_action2_triggered(self): #打开"各页面链接"文件
        f = self.name + "link_struct.txt"
        f_path = os.path.abspath(f_path)
        self.opentxtfile(f_path)

    @QtCore.pyqtSlot()
    def on_action3_triggered(self): #打开"各页面抓取范围内链接"文件
        f = self.name + "inlink_struct.txt"
        f_path = os.path.abspath(f_path)
        self.opentxtfile(f_path)

    @QtCore.pyqtSlot()
    def on_action4_triggered(self): #打开"各页面抓取范围外链接"文件
        f = self.name + "outlink_struct.txt"
        f_path = os.path.abspath(f_path)
        self.opentxtfile(f_path)

    def opencsvfile(self, f_path): #打开csv格式文件
        if os.path.exists(f_path):
            try:
                excel=win32com.client.Dispatch('Excel.Application')
                excel.Visible = 1
                excel.Workbooks.Open(f_path)
            except:
                QtGui.QMessageBox.about(self, u"无法打开文件", u"无法打开文件")
        else:
            QtGui.QMessageBox.about(self, u"请先生成统计结果", u"请先生成统计结果,点击分析菜单完成")

    @QtCore.pyqtSlot()
    def on_action5_triggered(self): #打开"站点的各类链接统计"文件
        f = self.name + "site links counts.csv"
        f_path = os.path.abspath(f_path)
        self.opencsvfile(f_path)

    @QtCore.pyqtSlot()
    def on_action6_triggered(self): #打开"站点间链接统计"文件
        f = self.name + "site counts from-to.csv"
        f_path = os.path.abspath(f_path)
        self.opencsvfile(f_path)

    @QtCore.pyqtSlot()
    def on_action7_triggered(self): #打开"站点间链接统计矩阵"文件
        f = self.name + "site matrix.csv"
        f_path = os.path.abspath(f_path)
        self.opencsvfile(f_path)

    @QtCore.pyqtSlot()
    def on_action8_triggered(self): #打开"页面的各类链接统计"文件
        f = self.name + "page links counts.csv"
        f_path = os.path.abspath(f_path)
        self.opencsvfile(f_path)

    @QtCore.pyqtSlot()
    def on_action9_triggered(self): #打开"页面间链接统计矩阵"文件
        f = self.name + "page matrix.csv"
        f_path = os.path.abspath(f_path)
        self.opencsvfile(f_path)

    @QtCore.pyqtSlot()
    def on_action10_triggered(self): #打开"页面间链接统计矩阵(去除全零行)"文件
        f = self.name + "page matrix strip.csv"
        f_path = os.path.abspath(f_path)
        self.opencsvfile(f_path)


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

