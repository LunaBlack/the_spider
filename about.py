# -*- coding: utf-8 -*-

import sys, os
from PyQt4 import QtCore, QtGui, uic


class about(QtGui.QDialog):
    def __init__(self):
        super(about, self).__init__()
        ui_about = uic.loadUi("about.ui", self)



