# -*- coding: utf-8 -*-

import sys, os
import logging
from PyQt4 import QtCore, QtGui, uic


class projectname(QtGui.QDialog):
    def __init__(self, name, logger):
        super(projectname, self).__init__()
        ui_projectname = uic.loadUi("projectname.ui", self)
        
        self.logger = logger
        self.name = name


    @QtCore.pyqtSlot()
    def on_okButton_clicked(self): #点击确定按钮
        text1 = self.projectnamelineEdit.text()
        text2 = unicode(text1.toUtf8(), "utf8").strip()

        try:
            text3 = text2.encode("ascii")
        except UnicodeEncodeError:
            QtGui.QMessageBox.about(self, u"格式错误", u"请重新输入项目名称")
        else:
            if not text3.isalnum():
                QtGui.QMessageBox.about(self, u"格式错误", u"请重新输入项目名称")
            else:
                self.name.append(text3)
                self.accept()


    @QtCore.pyqtSlot()
    def on_cancelButton_clicked(self): #点击取消按钮
        self.reject()





