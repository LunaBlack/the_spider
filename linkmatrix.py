#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle

class LinkMatrix():

    def __init__(self):
        pass

    def setroot(self, root):
        self.root = root
        self.forwardlinks = dict()
        for e in root:
            self.forwardlinks.setdefault(e, dict())

    def addLink(self, url, referer):
        #print(url, referer)
        try:
            if self.forwardlinks[referer].setdefault(url, 0):
                self.forwardlinks[referer][url] += 1
                return True
            else:
                self.forwardlinks[referer][url] += 1
                return False
        except KeyError:
            pass

    def store(self):
        with open("linkgraph", "w") as f:
            pickle.dump(self.forwardlinks, f)

    def load(self):
        with open("linkgraph", "r") as f:
            self.forwardlinks = pickle.load(f)

    def export_matrix(self):
        pass


