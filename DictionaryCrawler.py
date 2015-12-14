# -*- coding: utf-8 -*-
# @Date    : 2015-12-14 14:48:37
# @Author  : Lucien Zhou 

import re
import time
import string
import codecs
import random
import requests
import threading
from bs4 import BeautifulSoup


class DictionaryCrawler:
    """ Get the computer terms and corresponding definitions."""
    baseurl = 'http://www.webopedia.com'
    proxies = [{'http': 'http://182.92.155.193'},
               {'http': 'http://14.152.37.194:80'},
               {'http': 'http://27.191.234.69:9999'},
               {'http': 'http://27.115.75.114:8080'}]

    def __init__(self, alphabet):
        self.url = self.baseurl + '/TERM/' + alphabet
        self.proxy = self.proxies[random.randint(0, 3)]
        self.alphabet = alphabet
        self.term_url_list = []

    def get_terms_url(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content)
        for term_url in soup.find_all("li", {"class": re.compile('col.+?')}):
            term_url = self.baseurl + term_url.a['href']
            self.term_url_list.append(term_url)

    def get_html(self, url, proxy=None):
        s = requests.Session()
        s.headers['User-Agent'] = \
            'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36'
        try:
            r = s.post(url, proxies=proxy, timeout=10)
        except Exception, e:
            print str(e) + ' with proxy ' + url
            try:
                r = s.post(url, timeout=10)
            except:
                print "can't get the contents of " + url
        finally:
            return r.content

    def get_raw_paragraph(self, html):
        regex = r'<!--End related articles widget-->(.*)<div id="olal-container">'
        pattern = re.compile(regex, re.S)
        raw = re.findall(pattern, html)
        raw_paragraph = re.sub('</div>', '', raw[0])
        return raw_paragraph

    def get_definition(self):
        dic_file = codecs.open('F:/%s_terms.txt' % self.alphabet, 'w', "utf-8")
        global paragraph
        for url in self.term_url_list:

            while 1:
                try:
                    html = self.get_html(url, proxy=self.proxy)
                except:
                    break
                time.sleep(1)
                try:
                    paragraph = self.get_raw_paragraph(html)
                except:
                    re_html = self.get_html(url)  # in case the proxy can get the html, but which is incomplete
                    try:
                        paragraph = self.get_raw_paragraph(re_html)
                    except:
                        print " there is no definition in " + url
                        break
                else:
                    term = lambda url: url.split('/')[-1].split('.')[0]
                    print >> dic_file, term(url)
                    soup = BeautifulSoup(paragraph)
                    print >> dic_file, soup.get_text() + '\n'
                    print url
                break

        dic_file.close()

    def crawl(self):
        self.get_terms_url()
        self.get_definition()


def run(alphabet):
    instance = DictionaryCrawler(alphabet)
    instance.crawl()


index = string.uppercase
for i in xrange(26):
    t = threading.Thread(target=run, args=(index[i],))
    t.start()
