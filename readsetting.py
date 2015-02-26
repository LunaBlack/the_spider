# -*- coding: utf-8 -*-


class ReadSetting: #读取用户设置的信息,包括起始url、url获取规则、爬取和保存参数

    def __init__(self): #初始化,读取包含用户设置信息的文件
        #f = open("setting.txt", 'r')
        with open("setting.txt", 'r') as f:
            self.text = f.readlines()


    def projectname(self): #读取项目名
        projectname = ""
        for n,i in enumerate(self.text):
            if i.startswith("project name:"):
                m = n + 1
                projectname = self.text[m].strip()
                break
        return projectname


    def readurl(self): #读取起始url
        url = []
        for n,i in enumerate(self.text):
            if i.startswith("initial url:"):
                m = n + 1
                while self.text[m].strip() is not "":
                    url_temp = self.text[m].strip()
                    if  not url_temp.startswith("http://") and not url_temp.startswith("https://"):
                        url_temp = "http://%s/" % url_temp
                    url.append(url_temp)
                    m = m + 1
                break
        url = list(set(url))
        return url


    def readdomain(self): #读取指定的域名或路径
        domain = allow = deny = None

        for n,i in enumerate(self.text):
            if i.startswith("domain:"):
                m = n + 1
                while self.text[m].strip() is not "":
                    if self.text[m].startswith("allowed_domains="):
                        domain = eval(self.text[m][16:])
                    elif self.text[m].startswith("allow="):
                        allow = eval(self.text[m][6:])
                    elif self.text[m].startswith("deny="):
                        deny = eval(self.text[m][5:])
                    m = m + 1
                break

        if isinstance(domain, str):
            domain = (domain, )
        elif isinstance(domain, tuple):
            domain = tuple(set(domain))
        elif domain is None:
            domain = tuple()

        if isinstance(allow, str):
            allow = (allow, )
        elif isinstance(allow, tuple):
            allow = tuple(set(allow))
        elif allow is None:
            allow = tuple()

        if isinstance(deny, str):
            deny = (deny, )
        elif isinstance(deny, tuple):
            deny = tuple(set(deny))
        elif deny is None:
            deny = tuple()

        return (domain, allow, deny)


    def readxpath(self): #读取指定的Xpath表达式
        domain = url = ""

        for n,i in enumerate(self.text):
            if i.startswith("xpath:"):
                m = n + 1
                while self.text[m].strip() is not "":
                    if self.text[m].startswith("allowed_domains="):
                        domain = eval(self.text[m][16:])
                    elif self.text[m].startswith("url="):
                        url = eval(self.text[m][4:])
                    m = m + 1
                break

        if type(domain) == str:
            domain = [domain, ]
        else:
            domain = list(set(domain))

        return (domain, url)


    def pagenumber(self): #读取最大抓取页面数的参数
        pagenumber = 0
        for n,i in enumerate(self.text):
            if i.startswith("largest number of pages:"):
                m = n + 1
                pagenumber = int(self.text[m].strip())
                break
        return pagenumber


    def itemnumber(self): #读取最大爬取条目数的参数
        itemnumber = 0
        for n,i in enumerate(self.text):
            if i.startswith("largest number of items:"):
                m = n + 1
                itemnumber = int(self.text[m].strip())
                break
        return itemnumber


    def depth(self): #读取爬取深度的参数
        depth = 0
        for n,i in enumerate(self.text):
            if i.startswith("depth of crawling:"):
                m = n + 1
                depth = int(self.text[m].strip())
                break
        return depth


    def requesttime(self): #读取最大请求时间的参数
        requesttime = 180
        for n,i in enumerate(self.text):
            if i.startswith("longest time of requesting:"):
                m = n + 1
                requesttime = int(self.text[m].strip())
                break
        return requesttime


    def savinglocation(self): #读取文件保存位置
        savinglocation = ""
        for n,i in enumerate(self.text):
            if i.startswith("location of saving:"):
                m = n + 1
                savinglocation = unicode(self.text[m].strip(), 'utf8')
                break
        return savinglocation


    def savingname(self): #读取文件命名格式
        savingname = ""
        savingway = 0
        for n,i in enumerate(self.text):
            if i.startswith("naming of saving:"):
                m = n + 1
                savingname = self.text[m].strip()
                break
        if savingname == "顺序数字":
            savingway = 1
        elif savingname == "项目+顺序数字":
            savingway = 2
        elif savingname == "Html:Title":
            savingway = 3
        return savingway


    def savingformat(self): #读取文件保存格式
        savingformat = ""
        for n,i in enumerate(self.text):
            if i.startswith("format of saving:"):
                m = n + 1
                savingformat = self.text[m].strip()
                break
        return savingformat
