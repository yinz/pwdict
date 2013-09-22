#encoding=utf8

'''
    Author : Yin Zhu
    Date: Jun 9, 2013
'''

import urllib
import codecs
from BeautifulSoup import BeautifulSoup
from sys import argv
import re,time

class Translate:
    def Start(self):
        self._get_html_sourse()
        self._get_content("enc")
        self._remove_tag()
        self.print_result()

    def _get_html_sourse(self):
        word=argv[1] if len(argv)>1 else 'computer'
        url="http://dict.baidu.com/s?wd=%s&tn=dict" %  word
        self.htmlsourse=unicode(urllib.urlopen(url).read(),"gb2312","ignore").encode("utf-8","ignore")

    def _get_content(self,div_id):
        soup=BeautifulSoup("".join(self.htmlsourse))
        self.data=str(soup.find("div",{"id":div_id}))

    def _remove_tag(self):
        soup=BeautifulSoup(self.data)
        self.outtext=''.join([element  for element in soup.recursiveChildGenerator() if isinstance(element,unicode)])

    def print_result(self):
        for item in range(1,10):
            self.outtext=self.outtext.replace(str(item),"\n%s" % str(item))
        self.outtext=self.outtext.replace("  ","\n")
        print self.outtext

if __name__=="__main__":
     Translate().Start()