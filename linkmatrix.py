#!/usr/bin/env python
# encoding: utf-8

import cPickle as pickle
from urlparse import urlparse
import pprint
import codecs
import csv
import os

from readsetting import ReadSetting


class LinkMatrix():

    def __init__(self, projectname):
        self.projectname = projectname
        self.roots = []

        rs = ReadSetting()
        self.allowed_domains = rs.readalloweddomain()

        self.entire_struct = dict() #保存网站所有的页面结构，referer、url在爬取范围内，不一定符合抓取下载规则
        self.forwardlinks = dict() #保存所有下载下来的页面的页面的结构，referer、url符合抓取下载规则
        self.outlinks = dict() #记录所有的外链，referer符合抓取下载规则，url在抓取下载范围外


    def setroot(self, root): #将初始url加入到三个字典对象中(未修改)
        self.roots = root
        for e in self.roots:
            self.entire_struct.setdefault(e, set())
            self.forwardlinks.setdefault(e, dict())
            self.outlinks.setdefault(e, set())

        self.root_site = [urlparse(url).hostname for url in self.roots]

    def setIndexMap(self, index): #为所有页面编号
        self.indexmap = index

    def addLink(self, url, referer):
        if urlparse(url).hostname not in self.known_site:
            return True #not download

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

    def domain_links_count(self): #基于限制域的各类链接统计(所有下载条目均属于这些域)
        count = {}
        for domain in self.allowed_domains:
            count.setdefault(domain, {'Pages':0, 'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #Pages指属于该域的页面数
            #KnownLinks指下载范围内的页面;UnknownLinks指下载范围外的页面
            #InterLinks指条目对应的域内的页面;OutLinks指条目对应的域外的页面(包括下载范围外的页面)

        for k,v in self.forwardlinks.items():
            for domain in self.allowed_domains:
                if domain in k:
                    from_domain = domain
                    count[from_domain]['Pages'] += 1
                    break
            for t in v.keys():
                for domain in self.allowed_domains:
                    if domain in t:
                        to_domain = domain
                        if to_domain == from_domain:
                            count[from_domain]['InterLinks'] += 1
                        else:
                            count[from_domain]['OutLinks'] += 1
                        break
                count[from_host]['KnownLinks'] += 1

        for k,v in self.outlinks.items():
            for domain in self.allowed_domains:
                if domain in k:
                    from_domain = domain
                    break
            count[from_domain]['OutLinks'] += len(v)
            count[from_domain]['UnknownLinks'] += len(v)

        return count

    def site_links_count(self): #基于初始url对应站点的各类链接统计(部分下载条目可能不属于这些站点)
        count = {}
        for site in self.root_site:
            count.setdefault(site, {'Pages':0, 'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #Pages指站点包含的页面数
            #KnownLinks指下载范围内的页面;UnknownLinks指下载范围外的页面
            #InterLinks指本站点内的页面;OutLinks指本站点外的页面(包括下载范围外的页面)

        for k,v in self.forwardlinks.items():
            try:
                from_host = urlparse(k).hostname
                if from_host in self.root_site:
                    count[from_host]['Pages'] += 1
                    for t in v.keys():
                        to_host = urlparse(t).hostname
                        if to_host == from_host:
                            count[from_host]['InterLinks'] += 1
                        else:
                            count[from_host]['OutLinks'] += 1
                        count[from_host]['KnownLinks'] += 1
            except KeyError as err:
                print(err)

        for k,v in self.outlinks.items():
            try:
                from_host = urlparse(k).hostname
                if from_host in self.root_site:
                    count[from_host]['OutLinks'] += len(v)
                    count[from_host]['UnknownLinks'] += len(v)
            except KeyError as err:
                print(err)

        return count

    def page_links_count(self): #基于下载条目的各类链接统计
        count = {}
        for k,v in self.forwardlinks.items():
            from_host = urlparse(k).hostname
            count.setdefault(k, {'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #KnownLinks指下载范围内的页面;UnknownLinks指下载范围外的页面
            #InterLinks指条目对应的站点内的页面;OutLinks指条目对应的站点外的页面(包括下载范围外的页面)

            for t in v.keys():
                to_host = urlparse(t).hostname
                if to_host == from_host:
                    count[k]['InterLinks'] += 1
                else:
                    count[k]['OutLinks'] += 1
                count[k]['KnownLinks'] += 1

        for k,v in self.outlinks.items():
            count[k]['OutLinks'] += len(v)
            count[k]['UnknownLinks'] += len(v)

        return count

    def site_count_fromto(self): #基于初始url对应站点之间的链接统计(部分下载条目可能不属于这些站点)
        count = dict()
        for site in self.root_site:
            count.setdefault(site, dict())

        for e in self.forwardlinks.keys():
            from_host = urlparse(e).hostname
            if from_host in self.root_site:
                for t in self.forwardlinks[e].keys():
                    to_host = urlparse(t).hostname
                    if to_host in self.root_site:
                        count[from_host].setdefault(to_host, 0)
                        count[from_host][to_host] += 1

        return count

    def domain_count_fromto(self): #基于限制域之间的链接统计(所有下载条目均属于这些域)
        count = dict()
        for domain in self.allowed_domains:
            count.setdefault(domain, dict())

        for e in self.forwardlinks.keys():
            for domain in self.allowed_domains:
                if domain in e:
                    from_domain = domain
                    break
            for t in self.forwardlinks[e].keys():
                for domain in self.allowed_domains:
                    if domain in t:
                        to_domain = domain
                        break
                count[from_domain].setdefault(to_domain, 0)
                count[from_domain][to_domain] += 1

        return count


if __name__ == "__main__":
    lm = LinkMatrix("wlv")
    lm.load()
    lm.export_matrix()

