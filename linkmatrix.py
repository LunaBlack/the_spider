#!/usr/bin/env python
# encoding: utf-8

class LinkMatrix():

    def __init__(self, root):
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




