#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle
import pprint

class LinkMatrix():

    def __init__(self):
        pass

    def setroot(self, root):
        self.root = root
        self.forwardlinks = dict()
        self.outlinks = dict()
        for e in root:
            self.forwardlinks.setdefault(e, dict())
            self.outlinks.setdefault(e, set())

    def addLink(self, url, referer):
        try:
            if self.forwardlinks[referer].setdefault(url, 0):
                self.forwardlinks[referer][url] += 1
                return True
            else:
                self.forwardlinks[referer][url] += 1
                self.forwardlinks.setdefault(url, dict())
                self.outlinks.setdefault(url, set())
                return False
        except KeyError:
            print(url, referer)
            pprint.pprint(self.forwardlinks)
            return False

    def addOutLink(self, url, referer):
        try:
            self.outlinks[referer].add(url)
        except KeyError:
            print(url, referer)
            pprint.pprint(self.forwardlinks)
            return False

    def store(self):
        with open("linkgraph", "w") as f:
            pickle.dump(self.forwardlinks, f)
        with open("outlinkgraph", "w") as f:
            pickle.dump(self.outlinks, f)

    def load(self):
        with open("linkgraph", "r") as f:
            self.forwardlinks = pickle.load(f)
        with open("outlinkgraph", "r") as f:
            self.outlinks = pickle.load(f)

    def export_matrix(self):
        pass


