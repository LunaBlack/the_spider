def readurl(): #��ȡ��ʼurl
    f = open("setting.txt", 'r')
    text = f.readlines()
    url = []
    for n,i in enumerate(text):
        if i.startswith("initial url:"):
            m = n + 1
            while text[m] != '\n':
                url.append(text[m].strip())
                m = m + 1
            break
    url = list(set(url))
    return url


class AutoSpider():
    name = 'auto'
##    allowed_domains = ['mininova.org']
    start_urls = readurl()
    print start_urls
##    rules = [Rule(LinkExtractor(allow=['/tor/\d+']), 'parse_torrent')]

##    def readurl(self): #��ȡ��ʼurl
##        self.f = open("setting.txt", 'r')
##        text = f.readlines()
##        url = []
##        for n,i in enumerate(text):
##            if i.startswith("initial url:"):
##                m = n + 1
##                while text[m] != '\n':
##                    url.append(text[m])
##                    m = m + 1
##                break
##        url = list(set(url))
##        return url


##if __name__ == "__main__":
##    print("start")
##    test = AutoSpider()
##    print test.start_urls
    
    
