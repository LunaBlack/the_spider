#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle

class LinkMatrix():

    def __init__(self):
        pass

    def setroot(self, root):
        for e in root:
            self.forwardlinks = {e : set()}
            self.backwardlinks = {e : None}

    def addLink(self, url, referer):
        print(url, referer)
        if self.forwardlinks.has_key(referer):
            self.forwardlinks[referer].add(url)

            if self.forwardlinks.has_key(url):
                self.backwardlinks[url].add(referer)
                return True
            else:
                self.forwardlinks[url] = set()
                self.backwardlinks[url] = set()
                self.backwardlinks[url].add(referer)

            return False
        else:
            pass

    def store(self):
        with open("linkgraph", "w") as f:
            pickle.dump((self.forwardlinks, self.backwardlinks), f)

    def load(self):
        with open("linkgraph", "r") as f:
            (self.forwardlinks, self.backwardlinks) = pickle.load(f)

    def export_matrix(self):
        m =


