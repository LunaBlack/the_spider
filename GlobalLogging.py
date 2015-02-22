import logging


class NullHandler(logging.Handler):
    def emit(self, record): pass


class GlobalLogging:

    log = None
  
    @staticmethod
    def getInstance():
        if GlobalLogging.log == None: 
            GlobalLogging.log = GlobalLogging()
        return GlobalLogging.log 

    def __init__(self):
        self.logger = None
        self.handler = None
        self.level = logging.INFO
        self.logger = logging.getLogger("GlobalLogging")
        self.formatter = logging.Formatter("%(levelname)s - %(message)s")
        h = NullHandler()
        self.logger.addHandler(h)

    def setLoggingToFile(self,file):     
        fh = logging.FileHandler(file)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)
      
    def setLoggingToConsole(self) : 
        ch = logging.StreamHandler()
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
      
    def setLoggingToHanlder(self,handler): 
        self.handler = handler
      
    def setLoggingLevel(self,level):
        self.level = level
        self.logger.setLevel(level)
    
    def debug(self,s):
        self.logger.debug(s)
        if not self.handler == None and self.level <= logging.DEBUG :
            print logging.DEBUG
            print self.level
            self.handler('DEBUG:' + s)
    def info(self,s):
        self.logger.info(s)
        if not self.handler == None and self.level <= logging.INFO:
            self.handler('INFO:' + s)
    def warn(self,s):
        self.logger.warn(s)
        if not self.handler == None and self.level <= logging.WARNING:
            self.handler('WARN:' + s)
    def error(self,s):
        self.logger.error(s)
        if not self.handler == None and self.level <= logging.ERROR:
            self.handler('ERROR:' + s)
    def critical(self,s):
        self.logger.critical(s)
        if not self.handler == None and self.level <= logging.CRITICAL:
            self.handler('CRITICAL:' + s)
