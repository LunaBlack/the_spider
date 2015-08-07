#!/usr/bin/env python2
# encoding: utf-8

import sys
from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {"packages": 
                        ["os",
                        "twisted.internet",
			"zope.interface",
                        "scrapy",
                        "lxml",
                        "myproject",
			"statscollect",
                        "cryptography",
                        "distutils",
                        "email"],
    "excludes": ["tcl",
                "tk",
                "matplotlib",
                "wxPython"],
    "includes": ["OpenSSL.crypto"],
    "include_files": [("F:\\Scrapy test\\myproject\\UI\\scrapy.cfg","scrapy.cfg"),
        ("E:\\Python\\Python\\Lib\\site-packages\\scrapy\\VERSION","VERSION"),
        ("E:\\Python\\Python\\Lib\\site-packages\\scrapy\\mime.types","mime.types"),
	("main.ui", "main.ui"),
	("addurl.ui", "addurl.ui"),
        ("about.ui", "about.ui"),
	("projectname.ui", "projectname.ui"),
        ("moon.ico", "moon.ico"),
        ("Documentation.doc", "Documentation.doc"),
        ("Documentation.pdf", "Documentation.pdf"),]
    }

# GUI applications require a different base on Windows (the default is for a console application).

base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = "LunaSpider",
        version = "1.0",
        description = "LunaSpider", # "spider program for IM College"
        options = {"build_exe": build_exe_options},
        executables = [Executable("LunaSpider.py", base=base, icon="moon.ico")])
