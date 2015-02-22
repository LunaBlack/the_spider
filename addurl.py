# -*- coding: utf-8 -*-

import sys, os
import logging
from PyQt4 import QtCore, QtGui, uic


class addurl(QtGui.QDialog):
    def __init__(self, list_url, logger):
        super(addurl, self).__init__()
        ui_addurl = uic.loadUi("addurl.ui", self)
        
        self.logger = logger
        self.list_url = list_url
        
        self.siteformatlineEdit.textChanged.connect(self.batchinputpreview)
        self.wildcardpushButton.clicked.connect(self.batchinputpreview)
        self.arithmeticradioButton.clicked.connect(self.batchinputpreview)
        self.arithmeticfirstitemlineEdit.textChanged.connect(self.batchinputpreview)
        self.arithmeticitemnumberlineEdit.textChanged.connect(self.batchinputpreview)
        self.tolerancelineEdit.textChanged.connect(self.batchinputpreview)
        self.geometricradioButton.clicked.connect(self.batchinputpreview)
        self.geometricfirstitemlineEdit.textChanged.connect(self.batchinputpreview)
        self.geometricitemnumberlineEdit.textChanged.connect(self.batchinputpreview)
        self.ratiolineEdit.textChanged.connect(self.batchinputpreview)
        self.alphabeticallyradioButton.clicked.connect(self.batchinputpreview)
        self.alphameticallyfromlineEdit.textChanged.connect(self.batchinputpreview)
        self.alphameticallytolineEdit.textChanged.connect(self.batchinputpreview)

        
    def readsingleaddtext(self): #读取用户输入的单条网址
        self.logger.info("add single site")
        singleaddtext1 = self.singleaddplainTextEdit.toPlainText()
        text1 = singleaddtext1.split('\n')
        return text1


    def readbatchinputtext(self): #读取用户批量输入的网址
        self.logger.info("batch input sites")
        batchinputtext1 = self.batchinputpreviewtextBrowser.toPlainText()
        text1 = batchinputtext1.split('\n')
        return text1


    def readtextimporttext(self): #读取用户文本导入的网址
        self.logger.info("text import sites")
        textimporttext1 = self.textimportpreviewtextBrowser.toPlainText()
        text1 = textimporttext1.split('\n')
        return text1


    def readallurltext(self): #读取所有url的预览信息
        allurl1 = self.allurltextBrowser.toPlainText()
        text2 = allurl1.split('\n')
        return text2

    
    @QtCore.pyqtSlot()
    def on_singleaddButton_clicked(self): #逐条添加url
        text1 = self.readsingleaddtext()
        text2 = self.readallurltext()
        text = text1 + text2

        try:
            for e in text:
                temp = unicode(e.toUtf8(), "utf8").strip()
                temp = temp.encode("ascii")
        except UnicodeEncodeError:
            QtGui.QMessageBox.about(self, u"url格式错误", u"检测到含有中文或其它字符,请重新输入url")

        else:
            list_text1 = []
            for e in text:
                list_text1.append(str(e).strip())
            list_text2 = [e for e in list_text1 if e is not ""]
            
            number = 0
            list_text3 = []
            for e in list_text2:
                if e not in list_text3:
                    list_text3.append(e)
                else:
                    number = number + 1
            if number != 0:
                QtGui.QMessageBox.about(self, u"检测到重复", u"测试到%d条重复网址，已自动过滤" %number)

            urlpreview = '\n'.join(list_text3)
            self.logger.info("the url preview: %s" %list_text3)
            self.allurltextBrowser.setText(urlpreview)


    @QtCore.pyqtSlot()
    def on_wildcardpushButton_clicked(self): #用通配符*输入url格式
        text = self.siteformatlineEdit.text()[:self.siteformatlineEdit.cursorPosition()] + \
               "(*)" + self.siteformatlineEdit.text()[self.siteformatlineEdit.cursorPosition():]
        self.siteformatlineEdit.setText(text)

            
    def batchinputpreview(self): #预览批量输入的url
        list_text = []
        
        if self.arithmeticradioButton.isChecked(): #等差数列被选中
            try:
                temp = unicode(self.siteformatlineEdit.text().toUtf8(), "utf8").strip()
                temp = temp.encode("ascii")
            except UnicodeEncodeError:
                QtGui.QMessageBox.about(self, u"url格式错误", u"检测到含有中文或其它字符,请重新输入url")

            else:
                if (str(self.arithmeticfirstitemlineEdit.text()).isdigit() and str(self.arithmeticitemnumberlineEdit.text()).isdigit() \
                   and int(str(self.arithmeticitemnumberlineEdit.text())) > 0 and str(self.tolerancelineEdit.text()).isdigit()): #等差数列各项参数正确
                    firstitem = int(self.arithmeticfirstitemlineEdit.text())
                    itemnumber = number = int(self.arithmeticitemnumberlineEdit.text())
                    tolerance = int(self.tolerancelineEdit.text())
                    n = self.siteformatlineEdit.text().count("(*)")
                    
                    if n:
                        while(number):
                            s = str(self.siteformatlineEdit.text())
                            s = s.replace("(*)", str(firstitem + tolerance * (itemnumber - number)))
                            list_text.append(s)
                            number = number - 1
                else:
                    QtGui.QMessageBox.about(self, u"参数错误", u"请重新输入等差数列的参数")

        elif self.geometricradioButton.isChecked(): #等比数列被选中
            try:
                temp = unicode(self.siteformatlineEdit.text().toUtf8(), "utf8").strip()
                temp = temp.encode("ascii")
            except UnicodeEncodeError:
                QtGui.QMessageBox.about(self, u"url格式错误", u"检测到含有中文或其它字符,请重新输入url")

            else:
                if (str(self.geometricfirstitemlineEdit.text()).isdigit() and str(self.geometricitemnumberlineEdit.text()).isdigit() \
                    and int(str(self.geometricitemnumberlineEdit.text())) > 0 and str(self.ratiolineEdit.text()).isdigit()): #等比数列各项参数正确
                    firstitem = int(self.geometricfirstitemlineEdit.text())
                    itemnumber = number = int(self.geometricitemnumberlineEdit.text())
                    ratio = int(self.ratiolineEdit.text())
                    n = self.siteformatlineEdit.text().count("(*)")
                    
                    if n:
                        while(number):
                            s = str(self.siteformatlineEdit.text())
                            s = s.replace("(*)", str(firstitem * (ratio ** (itemnumber - number))))
                            list_text.append(s)
                            number = number - 1                    
                else:
                    QtGui.QMessageBox.about(self, u"参数错误", u"请重新输入等比数列的参数")

        elif self.alphabeticallyradioButton.isChecked(): #字母顺序被选中
            try:
                temp = unicode(self.siteformatlineEdit.text().toUtf8(), "utf8").strip()
                temp = temp.encode("ascii")
            except UnicodeEncodeError:
                QtGui.QMessageBox.about(self, u"url格式错误", u"检测到含有中文或其它字符,请重新输入url")

            else:
                if (str(self.alphameticallyfromlineEdit.text()).isalpha() and len(self.alphameticallyfromlineEdit.text()) == 1 \
                    and str(self.alphameticallytolineEdit.text()).isalpha() and len(self.alphameticallytolineEdit.text()) == 1 \
                    and ord(str(self.alphameticallytolineEdit.text()).strip()) >= ord(str(self.alphameticallyfromlineEdit.text()).strip())): #字母顺序各项参数正确
                    firstitem = ord(str(self.alphameticallyfromlineEdit.text()).strip())
                    lastitem = ord(str(self.alphameticallytolineEdit.text()).strip())
                    itemnumber = number = int(lastitem - firstitem + 1)
                    n = self.siteformatlineEdit.text().count("(*)")
                    
                    if n:
                        while(number):
                            s = str(self.siteformatlineEdit.text())
                            s = s.replace("(*)", str(chr(firstitem + (itemnumber - number))))
                            list_text.append(s)
                            number = number - 1                    
                else:
                    QtGui.QMessageBox.about(self, u"参数错误", u"请重新输入字母顺序的参数")

        text = '\n'.join(list_text)
        self.batchinputpreviewtextBrowser.setText(text)


    @QtCore.pyqtSlot()
    def on_batchinputButton_clicked(self): #批量输入url
        text1 = self.readbatchinputtext()
        text2 = self.readallurltext()
        text = text1 + text2

        try:
            for e in text:
                temp = unicode(e.toUtf8(), "utf8").strip()
                temp = temp.encode("ascii")
        except UnicodeEncodeError:
            QtGui.QMessageBox.about(self, u"url格式错误", u"检测到含有中文或其它字符,请重新输入url")

        else:
            list_text1 = []
            for e in text:
                list_text1.append(str(e).strip())
            list_text2 = [e for e in list_text1 if e is not ""]
            
            number = 0
            list_text3 = []
            for e in list_text2:
                if e not in list_text3:
                    list_text3.append(e)
                else:
                    number = number + 1
            if number != 0:
                QtGui.QMessageBox.about(self, u"检测到重复", u"测试到%d条重复网址，已自动过滤" %number)

            urlpreview = '\n'.join(list_text3)
            self.logger.info("the url preview: %s" %list_text3)
            self.allurltextBrowser.setText(urlpreview)


    @QtCore.pyqtSlot()
    def on_textimportlocationpushButton_clicked(self): #打开txt文件导入url预览
        filename = QtGui.QFileDialog.getOpenFileName(self, self.tr(""), QtCore.QString(), self.tr("Text Files(*.txt)"))
        s = unicode(filename.toUtf8(), "utf8")

        if s:
            f = open(s, 'r')
            text1 = f.readlines()
            f.close()

            self.textimportlocationlineEdit.setText(s)
            text2 = [e.strip() for e in text1]
            if text2:
                text3 = '\n'.join(text2)
                self.textimportpreviewtextBrowser.setText(text3)
            else:
                QtGui.QMessageBox.about(self, u"文本为空", u"文本中没有内容")


    @QtCore.pyqtSlot()
    def on_textimportButton_clicked(self): #文本导入url
        text1 = self.readtextimporttext()
        text2 = self.readallurltext()
        text = text1 + text2

        try:
            for e in text:
                temp = unicode(e.toUtf8(), "utf8").strip()
                temp = temp.encode("ascii")
        except UnicodeEncodeError:
            QtGui.QMessageBox.about(self, u"url格式错误", u"检测到含有中文或其它字符,请重新输入url")

        else:
            list_text1 = []
            for e in text:
                list_text1.append(str(e).strip())
            list_text2 = [e for e in list_text1 if e is not ""]
            
            number = 0
            list_text3 = []
            for e in list_text2:
                if e not in list_text3:
                    list_text3.append(e)
                else:
                    number = number + 1
            if number != 0:
                QtGui.QMessageBox.about(self, u"检测到重复", u"测试到%d条重复网址，已自动过滤" %number)

            urlpreview = '\n'.join(list_text3)
            self.logger.info("the url preview: %s" %list_text3)
            self.allurltextBrowser.setText(urlpreview)


    @QtCore.pyqtSlot()
    def on_okButton_clicked(self): #点击确定按钮
        text = str(self.allurltextBrowser.toPlainText())
        list_text = text.split('\n')
        for e in list_text:
            self.list_url.append(e)
        self.accept()


    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self): #点击取消按钮
        self.reject()




##    @QtCore.pyqtSlot()
##    def on_allurltextBrowser_customContextMenuRequested(point):
##        print "customContextMenu"
##        self.menu = QtGui.QMenu(self)
##        self.menu.addAction("Delete")



