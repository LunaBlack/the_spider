#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle
from urlparse import urlparse
import pprint
import codecs
import csv

class LinkMatrix():

    def __init__(self):
        self.roots = []
        self.forwardlinks = dict()
        self.backwardlinks = dict()
        self.outlinks = dict()

    def setroot(self, root):
        self.roots = root
        for e in self.roots:
            self.forwardlinks.setdefault(e, dict())
            self.backwardlinks.setdefault(e, None)
            self.outlinks.setdefault(e, set())

    def addLink(self, url, referer):
        try:
            if self.forwardlinks[referer].setdefault(url, 0):
                self.forwardlinks[referer][url] += 1

                self.backwardlinks[url].add(referer)
                return True
            else:
                self.forwardlinks[referer][url] += 1
                self.forwardlinks.setdefault(url, dict())

                self.backwardlinks.setdefault(url, set())
                self.backwardlinks[url].add(referer)

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
            #pprint.pprint(self.forwardlinks)
            return False

    def store(self):
        #import ipdb;ipdb.set_trace()
        with open("linkgraph", "w") as f:
            #pickle.dump((self.roots, self.forwardlinks,
            #    self.backwardlinks, self.outlinks), f)
            pickle.dump((self.roots, self.forwardlinks,
                self.outlinks), f)
        print("dumped")

    def load(self):
        with open("linkgraph", "r") as f:
            #self.roots, self.forwardlinks, self.backwardlinks, self.outlinks = pickle.load(f)
            self.roots, self.forwardlinks, self.outlinks = pickle.load(f)

    def export_matrix(self):
        page_count, out_count = self.pages_and_links_count()
        with codecs.open("page and link counts.csv", "w", "cp936") as f:
            fields = ["Site", "Pages", "Outlinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k in page_count.keys():
                row = {fields[0]:k, fields[1]:page_count[k], fields[2]:out_count[k]}
                print(row)
                writer.writerow(row)

        page_fromto_count = self.page_count_fromto()
        with codecs.open("file document counts from-to.csv", "w", "cp936") as f:
            fields = ["From", "To", "File Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in page_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    print(row)
                    writer.writerow(row)

    def iter_dfs(self, links, root):
        accessed, queue = set(), []
        queue.append(root)
        while queue:
            u = queue.pop()
            if u in accessed:
                continue
            accessed.add(u)
            queue.extend(links[u].keys())
            yield u

    def pages_and_links_count(self):
        #def find_root(link):
        #    for e in self.iter_dfs(self.backwardlinks, link):
        #        if e in self.roots:
        #            return e

        page_count = {}
        out_count = {}
        for root in self.roots:
            page_count.setdefault(urlparse(root).hostname, 0)
            out_count.setdefault(urlparse(root).hostname, 0)

        for e in self.forwardlinks.keys():
            #hostname = urlparse(root).hostname
            #links = [e for e in self.iter_dfs(self.forwardlinks, root)]
            #outlinks = [e for e in links if urlparse(e).hostname != hostname]
            #count[hostname] = len(links)
            #pprint.pprint(outlinks)
            try:
                page_count[urlparse(e).hostname] += 1
            except KeyError:
                pass

        for k,v in self.outlinks.items():
            try:
                out_count[urlparse(k).hostname] += len(v)
            except KeyError:
                pass

        return page_count, out_count

    def page_count_fromto(self):
        count = dict()

        for root in self.roots:
            count.setdefault(urlparse(root).hostname, dict())

        for e in self.forwardlinks.keys():
            from_host = urlparse(e).hostname
            for t in self.forwardlinks[e].keys():
                to_host = urlparse(t).hostname
                count[from_host].setdefault(to_host, 0)
                count[from_host][to_host] += 1

        return count

    def site_count_fromto(self):
        pass


if __name__ == "__main__":
    lm = LinkMatrix()
    lm.load()
    lm.export_matrix()

