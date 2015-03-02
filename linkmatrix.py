#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle
from urlparse import urlparse
import pprint
import codecs
import csv
import os

class LinkMatrix():

    def __init__(self, projectname):
        self.projectname = projectname
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

    def setIndexMap(self, index):
        self.indexmap = index

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
        try:
            print("Store", self.projectname)
            os.makedirs(self.projectname)
        except OSError as err:
            if err.errno != 17:
                raise err

        with open(self.projectname+"/page index.csv", "w") as f:
            fields = ["Index", "Url"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in self.indexmap.items():
                row = {"Index":v, "Url":k}
                writer.writerow(row)

        with open(self.projectname+"/linkgraph", "w") as f:
            #pickle.dump((self.roots, self.forwardlinks,
            #    self.backwardlinks, self.outlinks), f)
            pickle.dump((self.roots, self.forwardlinks,
                self.outlinks), f)

        print("dumped")

    def load(self):
        try:
            with open(self.projectname+"/linkgraph", "r") as f:
                #self.roots, self.forwardlinks, self.backwardlinks, self.outlinks = pickle.load(f)
                self.roots, self.forwardlinks, self.outlinks = pickle.load(f)

            with open(self.projectname+"/page index.csv", "r") as f:
                self.indexmap = {}
                reader = csv.DictReader(f)
                for e in reader:
                    self.indexmap.update({e["Url"]:e["Index"]})
        except IOError as err:
            raise err

    def export_matrix(self):
        try:
            os.mkdir(self.projectname)
        except OSError as e:
            if e.errno != 17:
                raise

        pages_count = self.pages_and_links_count()
        with open(self.projectname+"/page and link counts.csv", "w") as f:
            fields = ["Site", "Pages", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in pages_count.items():
                row = {fields[0]:k}
                row.update(v)
                print(row)
                writer.writerow(row)

        site_fromto_count = self.site_count_fromto()
        with open(self.projectname+"/site counts from-to.csv", "w") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in site_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    print(row)
                    writer.writerow(row)

        with codecs.open(self.projectname+"/site matrix.csv", "w", "cp936") as f:
            fields =["sites"] + [e for e in site_fromto_count.keys()]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k, v in site_fromto_count.items():
                row = {}
                [row.setdefault(k2, v2) for k2,v2 in v.items() if k2 in fields]
                row.update({"sites":k})
                for e in site_fromto_count.keys():
                    row.setdefault(e, 0)
                print(row)
                writer.writerow(row)

        domain_fromto_count = self.domain_count_fromto()
        with open(self.projectname+"/domain counts from-to.csv", "w") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in domain_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    print(row)
                    writer.writerow(row)

        with codecs.open(self.projectname+"/domain matrix.csv", "w", "cp936") as f:
            fields =["domains"] + [e for e in domain_fromto_count.keys()]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k, v in domain_fromto_count.items():
                row = {}
                [row.setdefault(k2, v2) for k2,v2 in v.items() if k2 in fields]
                row.update({"domains":k})
                for e in domain_fromto_count.keys():
                    row.setdefault(e, 0)
                print(row)
                writer.writerow(row)

        with open(self.projectname+"/link_struct.txt", "w") as f:
            lines = []
            for root in self.roots:
                for e in self.iter_dfs(self.forwardlinks, root):
                    if len(self.forwardlinks[e]) > 1:
                        lines.append(e+'\n')
                        for r in self.forwardlinks[e].keys():
                            lines.append("\t"+r+'\n')
                        lines.append('\n')
            f.writelines(lines)

        with open(self.projectname+"/outlink_struct.txt", "w") as f:
            lines = []
            for root in self.roots:
                for k,v in self.outlinks.items():
                    if len(v) > 1:
                        lines.append(k+'\n')
                        for r in v:
                            lines.append("\t"+r+'\n')
                        lines.append('\n')
            f.writelines(lines)

        with open(self.projectname+"/page matrix.csv", "w") as f:
            fields = ["from-to"] + [str(e) for e in range(1, len(self.indexmap)+1)]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for url,index in self.indexmap.items():
                for e,n in self.forwardlinks[url].items():
                    row = {"from-to":k}
                    [row.setdefault(str(i), 0) for i in range(1, len(self.indexmap)+1)]
                    row[self.indexmap[e]] = n
                    rows.append(row)
            writer.writerows(rows)

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

    def site_count_fromto(self):
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

    def domain_count_fromto(self):
        count = dict()
        for root in self.roots:
            domain = urlparse(root).hostname.split('.')[1]
            count.setdefault(domain, dict())

        for e in self.forwardlinks.keys():
            from_domain = urlparse(e).hostname.split('.')[1]
            for t in self.forwardlinks[e].keys():
                to_domain = urlparse(t).hostname.split('.')[1]
                count[from_domain].setdefault(to_domain, 0)
                count[from_domain][to_domain] += 1

        return count


if __name__ == "__main__":
    lm = LinkMatrix("wlv")
    lm.load()
    lm.export_matrix()

