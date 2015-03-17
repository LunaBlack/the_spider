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

        self.entire_struct = dict() #保存网站所有的页面结构,referer、url在爬取范围(限制域)内,不一定符合抓取下载规则
        self.forwardlinks = dict() #保存所有抓取下载范围内的页面的结构,referer、url符合抓取下载规则
        self.outlinks = dict() #记录所有的外链,referer符合抓取下载规则,url在抓取下载范围外(包括爬取范围外的页面)

        self.forwardlinks_0 = dict() #保存所有抓取下载范围内的页面的结构,referer不一定符合抓取下载规则,url符合抓取下载规则
        self.outlinks_0 = dict() #记录所有的外链,referer不一定符合抓取下载规则(但在爬取范围内),url在爬取范围(限制域)外

    def setroot(self, root): #将初始url加入到三个字典对象中,并初始化root_site对象
        self.roots = root
        for e in self.roots:
            if e.endswith('/'): #将url统一为不以'/'结尾的形式
                e = e[:-1]
            self.entire_struct.setdefault(e, set())
            self.forwardlinks_0.setdefault(e, dict())
            self.outlinks_0.setdefault(e, set())

        self.root_site = [urlparse(url).hostname for url in self.roots]

    def setIndexMap(self, index): #为符合下载条件的页面编号,index形式为{url:index}
        self.indexmap = index

    def addentirelink(self, url, referer): #构建entire_struct字典对象
        referer = referer.strip('/') #将链接统一为不以'/'结尾的形式
        url = url.strip('/')

        self.entire_struct.setdefault(referer, set())
        self.entire_struct[referer].add(url)
        self.entire_struct.setdefault(url, set())

    def addforwardlink(self, url, referer): #构建forwardlinks_0字典对象
        referer = referer.strip('/')
        url = url.strip('/')

        self.forwardlinks_0.setdefault(referer, dict())
        if url in self.forwardlinks_0[referer].keys():
            self.forwardlinks_0[referer][url] += 1
        else:
            self.forwardlinks_0[referer][url] = 1

    def addoutlink(self, url, referer): #构建outlinks_0字典对象
        referer = referer.strip('/')
        url = url.strip('/')

        self.outlinks_0.setdefault(referer, set())
        self.outlinks_0[referer].add(url)

    def structure_forwardlinks(self): #构建forwardlinks字典对象
        for k in self.indexmap.keys():
            self.forwardlinks.setdefault(k, dict())
            if k in self.forwardlinks_0.keys():
                self.forwardlinks[k] = self.forwardlinks_0[k]

    def structure_outlinks(self): #构建outlinks字典对象
        for k in self.indexmap.keys():
            self.outlinks.setdefault(k, set())
            for t in self.entire_struct[k]:
                if t and (t not in self.indexmap.keys()):
                    self.outlinks[k].add(t)
            if k in self.outlinks_0.keys():
                for e in self.outlinks_0[k]:
                    self.outlinks[k].add(e)

    def store(self): #以数据流形式将字典对象写入文件
        try:
            print("Store", self.projectname)
            os.makedirs(self.projectname) #创建以项目名命名的文件夹
        except OSError as err:
            if err.errno != 17:
                raise err

        with open(self.projectname+"/page index.csv", "wb") as f: #生成页面索引文件
            fields = ["Index", "Url"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in self.indexmap.items():
                row = {"Index":v, "Url":k}
                writer.writerow(row)

        with open(self.projectname+"/linkgraph", "wb") as f: #生成基本数据存储文件(包含范围数据和三个字典对象)
            pickle.dump((self.roots, self.root_site, self.allowed_domains, self.entire_struct, \
                self.forwardlinks_0, self.outlinks_0, self.forwardlinks, self.outlinks), f)

        print("dumped")

    def load(self): #以数据流形式从文件中读取字典对象
        try:
            with open(self.projectname+"/linkgraph", "r") as f:
                self.roots, self.root_site, self.allowed_domains, self.entire_struct, \
                    self.forwardlinks_0, self.outlinks_0, self.forwardlinks, self.outlinks = pickle.load(f)

            with open(self.projectname+"/page index.csv", "r") as f:
                self.indexmap = {}
                reader = csv.DictReader(f)
                for e in reader:
                    self.indexmap.update({e["Url"]:e["Index"]})
        except IOError as err:
            raise err

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
            count.setdefault(domain, {'Pages_1':0, 'Pages_2':0, 'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #Pages_1指属于该域的页面数(爬取范围内);Pages_2指属于该域的页面数(下载范围内)
            #KnownLinks链接指向下载范围内的页面;UnknownLinks链接指向下载范围外(包括爬取范围外)的页面
            #InterLinks链接指向条目对应的域内的页面(包括下载范围内外,即爬取范围内);OutLinks链接指向条目对应的域外的页面(包括下载范围外、爬取范围外的页面)

        for k in self.entire_struct.keys():
            for domain in self.allowed_domains:
                if domain in k:
                    from_domain = domain
                    count[from_domain]['Pages_1'] += 1
                    break
            if k in self.indexmap.keys():
                for t in self.entire_struct[k]:
                    for domain in self.allowed_domains:
                        if domain in t:
                            to_domain = domain
                            if to_domain == from_domain:
                                count[from_domain]['InterLinks'] += 1
                            else:
                                count[from_domain]['OutLinks'] += 1
                            break

        for k,v in self.forwardlinks.items():
            for domain in self.allowed_domains:
                if domain in k:
                    from_domain = domain
                    count[from_domain]['Pages_2'] += 1
                    break
            count[from_domain]['KnownLinks'] += len(v)

        for k,v in self.outlinks.items():
            for domain in self.allowed_domains:
                if domain in k:
                    from_domain = domain
                    break
            count[from_domain]['UnknownLinks'] += len(v)

        for k,v in self.outlinks_0.items():
            if k in self.indexmap.keys():
                for domain in self.allowed_domains:
                    if domain in k:
                        from_domain = domain
                        break
                count[from_domain]['OutLinks'] += len(v)

        return count

    def site_links_count(self): #基于初始url对应站点的各类链接统计(部分下载条目可能不属于这些站点)
        count = {}
        for site in self.root_site:
            count.setdefault(site, {'Pages_1':0, 'Pages_2':0, 'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #Pages_1指站点包含的页面数(爬取范围内);Pages_2指站点包含的页面数(下载范围内)
            #KnownLinks链接指向下载范围内的页面;UnknownLinks链接指向下载范围外的页面(包括爬取范围外)
            #InterLinks链接指向本站点内的页面(包括下载范围内外,即爬取范围内);OutLinks链接指向本站点外的页面(包括爬取范围内;及爬取范围外的所有页面)

        for k in self.entire_struct.keys():
            try:
                from_host = urlparse(k).hostname
                if from_host in self.root_site:
                    count[from_host]['Pages_1'] += 1
                    if k in self.indexmap.keys():
                        for t in self.entire_struct[k]:
                            try:
                                to_host = urlparse(t).hostname
                            except KeyError as err:
                                print(err)
                                count[from_host]['OutLinks'] += 1
                            else:
                                if to_host == from_host:
                                    count[from_host]['InterLinks'] += 1
                                else:
                                    count[from_host]['OutLinks'] += 1
            except KeyError as err:
                print(err)

        for k,v in self.forwardlinks.items():
            try:
                from_host = urlparse(k).hostname
                if from_host in self.root_site:
                    count[from_host]['Pages_2'] += 1
                    count[from_host]['KnownLinks'] += len(v)
            except KeyError as err:
                print(err)

        for k,v in self.outlinks.items():
            try:
                from_host = urlparse(k).hostname
                if from_host in self.root_site:
                    count[from_host]['UnknownLinks'] += len(v)
            except KeyError as err:
                print(err)

        for k,v in self.outlinks_0.items():
            if k in self.indexmap.keys():
                try:
                    from_host = urlparse(k).hostname
                    if from_host in self.root_site:
                        count[from_host]['OutLinks'] += len(v)
                except KeyError as err:
                    print(err)

        return count

    def page_links_count(self): #基于下载条目的各类链接统计
        count = {}
        for k,v in self.forwardlinks.items():
            from_host = urlparse(k).hostname
            count.setdefault(k, {'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #KnownLinks链接指向下载范围内的页面;UnknownLinks链接指向下载范围外的页面(包括爬取范围外)
            #InterLinks链接指向条目对应的站点内的页面(包括下载范围内外,即爬取范围内);OutLinks链接指向条目对应的站点外的页面(包括爬取范围内;及爬取范围外的所有页面)
            count[k]['KnownLinks'] += len(v)

        for k in self.entire_struct.keys():
            if k in self.indexmap.keys():
                from_host = urlparse(k).hostname
                for t in self.entire_struct[k]:
                    to_host = urlparse(t).hostname
                    if to_host == from_host:
                        count[k]['InterLinks'] += 1
                    else:
                        count[k]['OutLinks'] += 1

        for k,v in self.outlinks.items():
            count[k]['UnknownLinks'] += len(v)

        for k,v in self.outlinks_0.items():
            if k in self.indexmap.keys():
                count[k]['OutLinks'] += len(v)

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

    def export_downloadeditem_matrix(self): #生成基于下载条目的统计文件(包括链接陈列文件和各项统计矩阵)
        try:
            os.mkdir(self.projectname) #创建以项目名命名的文件夹
        except OSError as e:
            if e.errno != 17:
                raise
        
        domain_count = self.domain_links_count() #从统计函数中提取数据,作为本函数的基础数据
        site_count = self.site_links_count()
        page_count = self.page_links_count()
        site_fromto_count = self.site_count_fromto()
        domain_fromto_count = self.domain_count_fromto()

        #生成domain links counts.csv,即基于限制域的各类链接统计(所有下载条目均属于这些域)
        with open(self.projectname+"/domain links counts.csv", "wb") as f:
            fields = ["Domain ", "Pages_1", "Pages_2", "KnownLinks", "UnknownLinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in site_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        #生成site links counts.csv,即基于初始url对应站点的各类链接统计(部分下载条目可能不属于这些站点)
        with open(self.projectname+"/site links counts.csv", "wb") as f:
            fields = ["Site", "Pages_1", "Pages_2", "KnownLinks", "UnknownLinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in site_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        #生成page links counts.csv,即基于下载条目对应站点的各类链接统计
        with open(self.projectname+"/page links counts.csv", "wb") as f:
            fields = ["Page", "KnownLinks", "UnknownLinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in page_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        #生成domain counts from-to.csv,即基于限制域的链接统计(所有下载条目均属于这些域)
        with open(self.projectname+"/domain counts from-to.csv", "wb") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in domain_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    #print(row)
                    writer.writerow(row)

        #生成site counts from-to.csv,即基于初始url对应站点的链接统计(部分下载条目可能不属于这些站点)
        with open(self.projectname+"/site counts from-to.csv", "wb") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in site_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    #print(row)
                    writer.writerow(row)

        #生成domain matrix.csv,即基于限制域的链接统计矩阵(所有下载条目均属于这些域)
        with open(self.projectname+"/domain matrix.csv", "wb") as f:
            fields =["Domain"] + [e for e in self.allowed_domains]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k in fields[1:]:
                row = {"Domain":k}
                [row.setdefault(e, 0) for e in fields[1:]]
                for e,c in domain_fromto_count[k].items():
                    if e in fields:
                        row[e] = c
                #print(row)
                writer.writerow(row)

        #生成site matrix.csv,即基于初始url对应站点的链接统计矩阵(部分下载条目可能不属于这些站点)
        with open(self.projectname+"/site matrix.csv", "wb") as f:
            fields =["Site"] + [e for e in self.root_site]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k in fields[1:]:
                row = {"Site":k}
                [row.setdefault(e, 0) for e in fields[1:]]
                for e,c in site_fromto_count[k].items():
                    if e in fields:
                        row[e] = c
                #print(row)
                writer.writerow(row)

        #生成page matrix.csv,即基于下载条目的链接统计矩阵
        with open(self.projectname+"/page matrix.csv", "wb") as f:
            fields = ["Page"] + self.forwardlinks.keys()
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for k,v in self.forwardlinks.items():
                row = {"Page":k}
                [row.setdefault(i, 0) for i in self.forwardlinks.keys()]
                for e,n in v.items():
                    if n:
                        row[e] = 1 #存在链接即为1,不存在即为0
                rows.append(row)
            writer.writerows(rows)

        #生成page matrix strip.csv,即基于下载条目的链接统计矩阵(去除全零行)
        with open(self.projectname+"/page matrix strip.csv", "wb") as f:
            fields = ["Page"] + self.forwardlinks.keys()
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for k,v in self.forwardlinks.items():
                if len(v) >= 1:
                    row = {"Page":k}
                    [row.setdefault(i, 0) for i in self.forwardlinks.keys()]
                    for e,n in v.items():
                        if n:
                            row[e] = 1 #存在链接即为1,不存在即为0
                    rows.append(row)
            writer.writerows(rows)

        #生成link_struct.txt,即基于下载条目的链接列表(包括爬取范围内外的链接,即全部链接)
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

        #生成inlink_struct.txt,即基于下载条目的链接列表(包括下载范围内的链接)
        with open(self.projectname+"/inlink_struct.txt", "w") as f:
            lines = []
            for k,v in self.forwardlinks.items():
                if len(v) > 1:
                    lines.append(k+'\n')
                    for r in v.keys():
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

        #生成outlink_struct.txt,即基于下载条目的链接列表(包括下载范围外(含爬取范围外)的链接)
        with open(self.projectname+"/outlink_struct.txt", "w") as f:
            lines = []
            for k,v in self.outlinks.items():
                if len(v) > 1:
                    lines.append(k+'\n')
                    for r in v:
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

    def all_domain_links_count(self): #基于限制域的各类链接统计(所有爬取条目均属于这些域)
        count = {}
        for domain in self.allowed_domains:
            count.setdefault(domain, {'Pages':0, 'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #Pages指属于该域的页面数(爬取范围)
            #KnownLinks链接指向爬取范围(限制域)内的页面;UnknownLinks链接指向爬取范围(限制域)外的页面
            #InterLinks链接指向条目对应的域内的页面(包括下载范围内外,即爬取范围内);OutLinks链接指向条目对应的域外的页面(包括下载范围外、爬取范围外的页面)

        for k,v in self.entire_struct.items():
            for domain in self.allowed_domains:
                if domain in k:
                    from_domain = domain
                    count[from_domain]['Pages'] += 1
                    break
            for t in v:
                for domain in self.allowed_domains:
                    if domain in t:
                        to_domain = domain
                        if to_domain == from_domain:
                            count[from_domain]['InterLinks'] += 1
                        else:
                            count[from_domain]['OutLinks'] += 1
                        break
                count[from_domain]['KnownLinks'] += 1

        for k,v in self.outlinks_0.items():
            if k in self.entire_struct.keys():
                for domain in self.allowed_domains:
                    if domain in k:
                        from_domain = domain
                        break
                count[from_domain]['OutLinks'] += len(v)
                count[from_domain]['UnknownLinks'] += len(v)

        return count

    def all_site_links_count(self): #基于初始url对应站点的各类链接统计(部分爬取条目可能不属于这些站点,但在限制域内)
        count = {}
        for site in self.root_site:
            count.setdefault(site, {'Pages':0, 'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #Pages指站点包含的页面数(爬取范围)
            #KnownLinks链接指向爬取范围(限制域)内的页面;UnknownLinks链接指向爬取范围(限制域)外的页面
            #InterLinks链接指向本站点内的页面(包括下载范围内外,即爬取范围内);OutLinks链接指向本站点外的页面(包括爬取范围内;及爬取范围外的所有页面)

        for k,v in self.entire_struct.items():
            try:
                from_host = urlparse(k).hostname
                if from_host in self.root_site:
                    count[from_host]['Pages'] += 1
                    for t in v:
                        to_host = urlparse(t).hostname
                        if to_host == from_host:
                            count[from_host]['InterLinks'] += 1
                        else:
                            count[from_host]['OutLinks'] += 1
                        count[from_host]['KnownLinks'] += 1
            except KeyError as err:
                print(err)

        for k,v in self.outlinks_0.items():
            if k in self.entire_struct.keys():
                try:
                    from_host = urlparse(k).hostname
                    if from_host in self.root_site:
                        count[from_host]['OutLinks'] += len(v)
                        count[from_host]['UnknownLinks'] += len(v)
                except KeyError as err:
                    print(err)

        return count

    def all_page_links_count(self): #基于爬取条目的各类链接统计(所有爬取条目均属于限制域)
        count = {}
        for k,v in self.entire_struct.items():
            from_host = urlparse(k).hostname
            count.setdefault(k, {'KnownLinks':0, 'UnknownLinks':0, 'InterLinks':0, 'OutLinks':0})
            #KnownLinks链接指向爬取范围(限制域)内的页面;UnknownLinks链接指向爬取范围(限制域)外的页面
            #InterLinks链接指向条目对应的站点内的页面(包括下载范围内外,即爬取范围内);OutLinks链接指向条目对应的站点外的页面(包括爬取范围内;及爬取范围外的所有页面)

            for t in v:
                to_host = urlparse(t).hostname
                if to_host == from_host:
                    count[k]['InterLinks'] += 1
                else:
                    count[k]['OutLinks'] += 1
                count[k]['KnownLinks'] += 1

        for k,v in self.outlinks_0.items():
            if k in self.entire_struct.keys():
                count[k]['OutLinks'] += len(v)
                count[k]['UnknownLinks'] += len(v)

        return count

    def all_site_count_fromto(self): #基于初始url对应站点之间的链接统计(部分爬取条目可能不属于这些站点,但在限制域内)
        count = dict()
        for site in self.root_site:
            count.setdefault(site, dict())

        for e in self.entire_struct.keys():
            from_host = urlparse(e).hostname
            if from_host in self.root_site:
                for t in self.entire_struct[e]:
                    to_host = urlparse(t).hostname
                    if to_host in self.root_site:
                        count[from_host].setdefault(to_host, 0)
                        count[from_host][to_host] += 1

        return count

    def all_domain_count_fromto(self): #基于限制域之间的链接统计(所有爬取条目均属于这些域)
        count = dict()
        for domain in self.allowed_domains:
            count.setdefault(domain, dict())

        for e in self.entire_struct.keys():
            for domain in self.allowed_domains:
                if domain in e:
                    from_domain = domain
                    break
            for t in self.entire_struct[e]:
                for domain in self.allowed_domains:
                    if domain in t:
                        to_domain = domain
                        break
                count[from_domain].setdefault(to_domain, 0)
                count[from_domain][to_domain] += 1

        return count

    def export_allitem_matrix(self): #生成基于爬取条目的统计文件(包括链接陈列文件和各项统计矩阵)
        try:
            os.mkdir(self.projectname) #创建以项目名命名的文件夹
        except OSError as e:
            if e.errno != 17:
                raise

        all_domain_count = self.all_domain_links_count() #从统计函数中提取数据,作为本函数的基础数据
        all_site_count = self.all_site_links_count()
        all_page_count = self.all_page_links_count()
        all_site_fromto_count = self.all_site_count_fromto()
        all_domain_fromto_count = self.all_domain_count_fromto()

        #生成all domain links counts.csv,即基于限制域的各类链接统计(所有爬取条目均属于这些域)
        with open(self.projectname+"/all domain links counts.csv", "wb") as f:
            fields = ["Domain ", "Pages", "KnownLinks", "UnknownLinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in all_site_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        #生成all site links counts.csv,即基于初始url对应站点的各类链接统计(部分爬取条目可能不属于这些站点,但在限制域内)
        with open(self.projectname+"/all site links counts.csv", "wb") as f:
            fields = ["Site", "Pages", "KnownLinks", "UnknownLinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in all_site_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        #生成all page links counts.csv,即基于下载条目对应站点的各类链接统计
        with open(self.projectname+"/all page links counts.csv", "wb") as f:
            fields = ["Page", "KnownLinks", "UnknownLinks", "InterLinks", "OutLinks"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in all_page_count.items():
                row = {fields[0]:k}
                row.update(v)
                #print(row)
                writer.writerow(row)

        #生成all domain counts from-to.csv,即基于限制域的链接统计(所有爬取条目均属于这些域)
        with open(self.projectname+"/all domain counts from-to.csv", "wb") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in all_domain_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    #print(row)
                    writer.writerow(row)

        #生成all site counts from-to.csv,即基于初始url对应站点的链接统计(部分爬取条目可能不属于这些站点,但在限制域内)
        with open(self.projectname+"/all site counts from-to.csv", "wb") as f:
            fields = ["From", "To", "Links"]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k,v in all_site_fromto_count.items():
                for e,c in v.items():
                    row = {fields[0]:k, fields[1]:e, fields[2]:c}
                    #print(row)
                    writer.writerow(row)

        #生成all domain matrix.csv,即基于限制域的链接统计矩阵(所有爬取条目均属于这些域)
        with open(self.projectname+"/all domain matrix.csv", "wb") as f:
            fields =["Domain"] + [e for e in self.allowed_domains]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k in fields[1:]:
                row = {"Domain":k}
                [row.setdefault(e, 0) for e in fields[1:]]
                for e,c in all_domain_fromto_count[k].items():
                    if e in fields:
                        row[e] = c
                #print(row)
                writer.writerow(row)

        #生成all site matrix.csv,即基于初始url对应站点的链接统计矩阵(部分爬取条目可能不属于这些站点,但在限制域内)
        with open(self.projectname+"/all site matrix.csv", "wb") as f:
            fields =["Site"] + [e for e in self.root_site]
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            for k in fields[1:]:
                row = {"Site":k}
                [row.setdefault(e, 0) for e in fields[1:]]
                for e,c in all_site_fromto_count[k].items():
                    if e in fields:
                        row[e] = c
                #print(row)
                writer.writerow(row)

        #生成all page matrix.csv,即基于爬取条目的链接统计矩阵
        with open(self.projectname+"/all page matrix.csv", "wb") as f:
            fields = ["Page"] + self.entire_struct.keys()
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for k,v in self.entire_struct.items():
                row = {"Page":k}
                [row.setdefault(i, 0) for i in self.entire_struct.keys()]
                for e in v:
                    row[e] = 1 #存在链接即为1,不存在即为0
                rows.append(row)
            writer.writerows(rows)

        #生成all page matrix strip.csv,即基于爬取条目的链接统计矩阵(去除全零行)
        with open(self.projectname+"/all page matrix strip.csv", "wb") as f:
            fields = ["Page"] + self.entire_struct.keys()
            writer = csv.DictWriter(f, fieldnames = fields)
            writer.writeheader()
            rows = []
            for k,v in self.entire_struct.items():
                if len(v) >= 1:
                    row = {"Page":k}
                    [row.setdefault(i, 0) for i in self.entire_struct.keys()]
                    for e in v:
                        row[e] = 1 #存在链接即为1,不存在即为0
                    rows.append(row)
            writer.writerows(rows)

        #生成all_link_struct.txt,即基于爬取条目的链接列表(包括爬取范围内外的链接,即全部链接)
        with open(self.projectname+"/all_link_struct.txt", "w") as f:
            lines = []
            for k,v in self.entire_struct.items():
                if len(v) > 1 or ( k in self.outlinks_0.keys()):
                    lines.append(k+'\n')
                    for r in v:
                        lines.append("\t"+r+'\n')
                    for r in self.outlinks_0[k]:
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

        #生成all_inlink_struct.txt,即基于爬取条目的链接列表(包括爬取范围内的链接)
        with open(self.projectname+"/all_inlink_struct.txt", "w") as f:
            lines = []
            for k,v in self.entire_struct.items():
                if len(v) > 1:
                    lines.append(k+'\n')
                    for r in v:
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)

        #生成all_outlink_struct.txt,即基于爬取条目的链接列表(包括爬取范围外的链接)
        with open(self.projectname+"/all_outlink_struct.txt", "w") as f:
            lines = []
            for k,v in self.outlinks_0.items():
                if k in self.entire_struct.keys() and len(v) > 1:
                    lines.append(k+'\n')
                    for r in v:
                        lines.append("\t"+r+'\n')
                    lines.append('\n')
            f.writelines(lines)


if __name__ == "__main__":
    lm = LinkMatrix("im")
    lm.load()
    lm.export_downloadeditem_matrix()
    lm.export_allitem_matrix()

