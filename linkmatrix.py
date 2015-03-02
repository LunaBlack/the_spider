#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle
from urlparse import urlparse
import pprint
import codecs
import csv
import os

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

    def export_matrix(self, projectname):
        try:
            os.mkdir(projectname)
        except OSError as e:
            if e.errno == 17:
                pass

        pages_count = self.pages_and_links_count()
        with codecs.open(projectname+"/page and link counts.csv", "w", "cp936") as f:
            fields = ["Site", "Pages", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in pages_count.items():
                row = {fields[0]:k}
                row.update(v)
                print(row)
                writer.writerow(row)

        page_fromto_count = self.page_count_fromto()
        with codecs.open(projectname+"/page counts from-to1.csv", "w", "cp936") as f:
            fields = ["From", "To", "File Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in page_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    print(row)
                    writer.writerow(row)

        with codecs.open(projectname+"/page counts from-to2.csv", "w", "cp936") as f:
            fields =["sites"] + [e for e in page_fromto_count.keys()]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k, v in page_fromto_count.items():
                row = {}
                [row.setdefault(k2, v2) for k2,v2 in v.items() if k2 in fields]
                row.update({"sites":k})
                for e in page_fromto_count.keys():
                    row.setdefault(e, 0)
                print(row)
                writer.writerow(row)

        lines = []
        for root in self.roots:
            for e in self.iter_dfs(self.forwardlinks, root):
                if len(self.forwardlinks[e]) > 1:
                    lines.append(e+'\n')
                    for r in self.forwardlinks[e].keys():
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
        with open(projectname+"/link_struct.txt", "w") as f:
            f.writelines(lines)


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
        count = {}
        known_site = [urlparse(url).hostname for url in self.roots]
        for root in self.roots:
            hostname = urlparse(root).hostname
            count.setdefault(hostname, {'Pages':0, 'InterLinks':0, 'OutLinks':0})
            for e in self.iter_dfs(self.forwardlinks, root):
                for l in self.forwardlinks[e].keys():
                    if urlparse(l).hostname in known_site:
                        count[hostname]['InterLinks'] += 1

        for e in self.forwardlinks.keys():
            try:
                count[urlparse(e).hostname]['Pages'] += 1
            except KeyError:
                pass

        for k,v in self.outlinks.items():
            try:
                count[urlparse(k).hostname]['OutLinks'] += len(v)
            except KeyError:
                pass

        return count

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
        count = dict()
        for root in self.roots:
            count.setdefault(urlparse(root).hostname, dict())

        for e in self.forwardlinks.keys():
            pass


if __name__ == "__main__":
    lm = LinkMatrix()
    lm.load()
    lm.export_matrix("im")

