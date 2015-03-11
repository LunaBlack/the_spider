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

        with open(self.projectname+"/page index.csv", "wb") as f:
            fields = ["Index", "Url"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in self.indexmap.items():
                row = {"Index":v, "Url":k}
                writer.writerow(row)

        with open(self.projectname+"/linkgraph", "wb") as f:
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

        site_count = self.site_links_count()
        with open(self.projectname+"/site links counts.csv", "wb") as f:
            fields = ["Site", "Pages", "Knowlinks", "Unknowlinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in site_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        page_count = self.page_links_count()
        with open(self.projectname+"/page links counts.csv", "wb") as f:
            fields = ["Page", "Knowlinks", "Unknowlinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in page_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)


        site_fromto_count = self.site_count_fromto()
        #pprint.pprint(site_fromto_count)
        with open(self.projectname+"/site counts from-to.csv", "wb") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in site_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    #print(row)
                    writer.writerow(row)

        with open(self.projectname+"/site matrix.csv", "wb") as f:
            fields =["sites"] + [urlparse(e).hostname for e in self.roots]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k in fields[1:]:
                row = {"sites":k}
                [row.setdefault(e, 0) for e in fields[1:]]
                for e,c in site_fromto_count[k].items():
                    if e in fields:
                        row[e] = c
                #print(row)
                writer.writerow(row)

        with open(self.projectname+"/link_struct.txt", "w") as f:
            lines = []
            for k,v in self.forwardlinks.items():
                if len(v) > 1 or len(self.outlinks[k]) > 1:
                    lines.append(k+'\n')
                    for r in v.keys():
                        lines.append("\t"+r+'\n')
                    for r in self.outlinks[k]:
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

        with open(self.projectname+"/inlink_struct.txt", "w") as f:
            lines = []
            for k,v in self.forwardlinks.items():
                if len(v) > 1:
                    lines.append(e+'\n')
                    for r in v.keys():
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

        with open(self.projectname+"/outlink_struct.txt", "w") as f:
            lines = []
            for k,v in self.outlinks.items():
                if len(v) > 1:
                    lines.append(k+'\n')
                    for r in v:
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

        with open(self.projectname+"/page matrix.csv", "wb") as f:
            fields = ["from-to"] + self.forwardlinks.keys()
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for k,v in self.forwardlinks.items():
                row = {"from-to":k}
                [row.setdefault(i, 0) for i in self.forwardlinks.keys()]
                for e,n in v.items():
                    row[e] = n
                rows.append(row)
            writer.writerows(rows)

        with open(self.projectname+"/page matrix strip.csv", "wb") as f:
            fields = ["from-to"] + self.forwardlinks.keys()
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for k,v in self.forwardlinks.items():
                if len(v) >= 1:
                    row = {"from-to":k}
                    [row.setdefault(i, 0) for i in self.forwardlinks.keys()]
                    for e,n in v.items():
                        row[e] = n
                    rows.append(row)
            writer.writerows(rows)

    def iter_dfs(self, links, root): #深度优先遍历,生成链接链(暂时无用)
        accessed, queue = set(), []
        queue.append(root)
        while queue:
            u = queue.pop()
            if u in accessed:
                continue
            accessed.add(u)
            queue.extend(links[u].keys())
            yield u

    def site_links_count(self):
        count = {}
        known_site = [urlparse(url).hostname for url in self.roots]
        for root in self.roots:
            hostname = urlparse(root).hostname
            count.setdefault(hostname, {'Pages':0, 'Knowlinks':0, 'Unknowlinks':0, 'InterLinks':0, 'OutLinks':0})
            #for e in self.iter_dfs(self.forwardlinks, root):
            #    for l in self.forwardlinks[e].keys():
            #        if urlparse(l).hostname in known_site:
            #            count[hostname]['InterLinks'] += 1

        for k,v in self.forwardlinks.items():
            try:
                from_host = urlparse(k).hostname
                count[from_host]['Pages'] += 1
                for t in v.keys():
                    to_host = urlparse(t).hostname
                    if to_host == from_host:
                        count[from_host]['InterLinks'] += 1
                    else:
                        count[from_host]['OutLinks'] += 1
                    if to_host in known_site:
                        count[from_host]['Knowlinks'] += 1
                    else:
                        count[from_host]['Unknowlinks'] += 1
            except KeyError as err:
                print(err)

        for k,v in self.outlinks.items():
            try:
                count[urlparse(k).hostname]['OutLinks'] += len(v)
                count[urlparse(k).hostname]['Unknowlinks'] += len(v)
            except KeyError as err:
                print(err)

        return count

    def page_links_count(self):
        count = {}
        known_site = [urlparse(url).hostname for url in self.roots]
        for k,v in self.forwardlinks.items():
            from_host = urlparse(k).hostname
            count.setdefault(k, {'Knowlinks':0, 'Unknowlinks':0, 'InterLinks':0, 'OutLinks':0})
            for t in v.keys():
                to_host = urlparse(t).hostname
                if to_host == from_host:
                    count[k]['InterLinks'] += 1
                else:
                    count[k]['OutLinks'] += 1
                if to_host in known_site:
                    count[k]['Knowlinks'] += 1
                else:
                    count[k]['Unknowlinks'] += 1

        for k,v in self.outlinks.items():
            count[k]['OutLinks'] += len(v)
            count[k]['Unknowlinks'] += len(v)

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

    def domain_count_fromto(self): #(暂时无用)
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

