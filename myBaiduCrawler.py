#!/usr/bin/env python
# _*_ coding:utf-8 _*_
"""
 * @author: Lightwing Ng
 * email: rodney_ng@iCloud.com
 * created on May 02, 2018, 7:52 AM
 * Software: PyCharm
 * Project Name: Tutorial
"""

import urllib, urllib2
import re
import datetime


class Tool:
    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    replaceTD = re.compile('<td>')
    replacePara = re.compile('<p.*?>')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, '', x)
        x = re.sub(self.removeAddr, '', x)
        x = re.sub(self.replaceLine, '\n', x)
        x = re.sub(self.replaceTD, '\t', x)
        x = re.sub(self.replacePara, '\n    ', x)
        x = re.sub(self.replaceBR, '\n', x)
        x = re.sub(self.removeExtraTag, '', x)

        return x.strip()


class BaiduTieba:
    def __init__(self, baseUrl, seeLZ, floorTag):
        self.baseURL = baseUrl
        self.seeLZ = '?see_lz=' + str(seeLZ)
        self.tool = Tool()
        self.file = None
        self.floor = 1
        self.defaultTitle = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.floorTag = floorTag

    def getPage(self, pageNum):
        try:
            url = self.baseURL + self.seeLZ + '&pn=' + str(pageNum)
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)

            return response.read().decode('UTF-8')
        except urllib2.URLError, e:
            if hasattr(e, 'reason'):
                print(u'Lost Connection for: ', e.reason)
                return None

    def getTitle(self, page):
        pattern = re.compile('<h1 class="core_title_txt.*?>(.*?)</h1>', re.S)
        result = re.search(pattern, page)
        if result:
            return result.group(1).strip()
        else:
            return None

    def getPageNum(self, page):
        pattern = re.compile('<li class="l_reply_num.*?</span>.*?<span.*?>(.*?)</span>', re.S)
        result = re.search(pattern, page)
        if result:
            return result.group(1).strip()
        else:
            return None

    def getContent(self, page):
        pattern = re.compile('<div id="post_content_.*?>(.*?)</div>', re.S)
        items = re.findall(pattern, page)
        contents = []
        for x in items:
            content = '\n' + self.tool.replace(x) + '\n'
            contents.append(content.encode('UTF-8'))
        return contents

    def setFileTitle(self, title):
        if title is not None:
            self.file = open(title + '.txt', 'w+')
        else:
            self.file = open(self.defaultTitle + '.txt', 'w+')

    def writeData(self, contents):
        for x in contents:
            if self.floorTag == '1':
                floorLine = str(self.floor).center(50, '-')
                self.file.write(floorLine)
            self.file.write(x)
            self.floor += 1

    def run(self):
        indexPage = self.getPage(1)
        pageNum = self.getPageNum(indexPage)
        title = self.getTitle(indexPage)
        self.setFileTitle(title)

        if pageNum == None:
            print(u'Invalid URL, Please try again.')
            return
        try:
            print(u'The Mission of 「%s」has totally %d Pages' % (title, int(pageNum)))
            for x in range(1, int(pageNum) + 1):
                print('Writing to Page %d/%d.' % (int(x), int(pageNum)))
                page = self.getPage(x)
                contents = self.getContent(page)
                self.writeData(contents)
        except IOError, e:
            print(u'Error of: ', e.message)
        finally:
            print(u'Mission of %s has been done!' % title)


f = open('URLs.txt')

for x in f:
    task = BaiduTieba(x.strip(), 0, 0)
    task.run()
