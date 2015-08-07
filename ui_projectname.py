# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'projectname.ui'
#
# Created: Fri Jul 10 02:40:26 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_projectnemaDialog(object):
    def setupUi(self, projectnemaDialog):
        projectnemaDialog.setObjectName(_fromUtf8("projectnemaDialog"))
        projectnemaDialog.setWindowModality(QtCore.Qt.ApplicationModal)
        projectnemaDialog.resize(414, 124)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(projectnemaDialog.sizePolicy().hasHeightForWidth())
        projectnemaDialog.setSizePolicy(sizePolicy)
        projectnemaDialog.setMinimumSize(QtCore.QSize(414, 124))
        projectnemaDialog.setMaximumSize(QtCore.QSize(414, 124))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("moon.ico")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        projectnemaDialog.setWindowIcon(icon)
        projectnemaDialog.setModal(True)
        self.projectnamelabel = QtGui.QLabel(projectnemaDialog)
        self.projectnamelabel.setGeometry(QtCore.QRect(20, 10, 301, 23))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.projectnamelabel.setFont(font)
        self.projectnamelabel.setObjectName(_fromUtf8("projectnamelabel"))
        self.projectnamelineEdit = QtGui.QLineEdit(projectnemaDialog)
        self.projectnamelineEdit.setGeometry(QtCore.QRect(40, 42, 331, 26))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.projectnamelineEdit.setFont(font)
        self.projectnamelineEdit.setObjectName(_fromUtf8("projectnamelineEdit"))
        self.okButton = QtGui.QPushButton(projectnemaDialog)
        self.okButton.setGeometry(QtCore.QRect(100, 83, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.okButton.setFont(font)
        self.okButton.setObjectName(_fromUtf8("okButton"))
        self.cancelButton = QtGui.QPushButton(projectnemaDialog)
        self.cancelButton.setGeometry(QtCore.QRect(240, 83, 75, 23))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.cancelButton.setFont(font)
        self.cancelButton.setObjectName(_fromUtf8("cancelButton"))

        self.retranslateUi(projectnemaDialog)
        QtCore.QMetaObject.connectSlotsByName(projectnemaDialog)

    def retranslateUi(self, projectnemaDialog):
        projectnemaDialog.setWindowTitle(_translate("projectnemaDialog", "项目名称", None))
        self.projectnamelabel.setText(_translate("projectnemaDialog", "请输入项目名称（请用字母与数字表达）：", None))
        self.okButton.setText(_translate("projectnemaDialog", "确定", None))
        self.cancelButton.setText(_translate("projectnemaDialog", "取消", None))

