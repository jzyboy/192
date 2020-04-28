#!/usr/bin/env python
# coding: utf-8

# 语雀题目链接：https://www.yuque.com/ol1q37/gi94xp/vy59wr
# Pony链接：https://editor.ponyorm.com/user/peiban/Tm/designer
# 数据库链接：链接：https://pan.baidu.com/s/1nPT4bl2YlFQsClslVuSvsg 提取码：jksq

from pony.orm import *
import requests,time,re,os
from selenium import webdriver
from lxml import etree

# 创建数据库
db = Database()
class Tm(db.Entity):
    id = PrimaryKey(int, auto=True)
    bh = Optional(str)
    bt = Optional(str)
    fs = Optional(int)
    tgs = Optional(int)
    tjs = Optional(int)
    tgl = Optional(float)
    tmnl = Optional(str)
    html = Optional(str)
    tx = Optional(str)
    xqylj = Optional(str)

def task1():
    '''对数据库的处理'''
    # 在指定路径下创建名为star.sqlite的数据库
    dbpath = r'E:\python\Tm.sqlite'
    # 如果该数据库在此路径下存在则将原来的数据库删除并创建新的数据库
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath,'w')
    f.close()
    db.bind(provider = 'sqlite', filename = 'E:/python/Tm.sqlite')
    db.generate_mapping(create_tables = True)
    set_sql_debug(True)

def _get_html(url):
    '''获取网页源代码'''
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    return html

def _get_url():
    urls = ['https://pintia.cn/problem-sets/1111652100718116864/problems/type/7','https://pintia.cn/problem-sets/1111652100718116864/problems/type/6']
    return urls

def _get_bh(html):
    '''爬取该网页题目标号'''
    bhs = []
    reobj = re.compile(r'<tr><td class="answerIcon_1du7d"></td><td>([\d\D]*?)</td><td><a href=[\d\D]*?')
    for match in reobj.finditer(html):
        bhs.append(match.group(1))
    return bhs

def _get_tx(html):
    '''爬取该网页题型并入库'''
    match = re.search(r'class="nav-link active">[\d\D]*?class="pc-text-raw">([\d\D]*?)</div></div><span', html)
    if match:
        txs = match.group(1)
    return txs

def _get_bt(html):
    '''爬取该网页标题'''
    bts = []
    reobj = re.compile(r'<td><a href="[\d\D]*?class="">([\d\D]*?)</a></td>')
    for match in reobj.finditer(html):
        bts.append(match.group(1))
    return bts

def _get_fs(html):
    '''爬取该网页分数'''
    fss = []
    reobj = re.compile(r'class="answerIcon_1du7d"></td><td>[\d\D]*?href="[\d\D]*?</a></td><td>([\d\D]*?)</td><td>')
    for match in reobj.finditer(html):
        fss.append(match.group(1))
    return fss

def _get_tgs(html):
    '''爬取该网页通过数'''
    tgss = []
    reobj = re.compile(r'class="answerIcon_1du7d"></td><td>[\d\D]*?href="[\d\D]*?</a></td><td>[\d\D]*?</td><td>([\d\D]*?)</td><td>')
    for match in reobj.finditer(html):
        tgss.append(match.group(1))
    return tgss

def _get_tjs(html):
    '''爬取该网页提交数'''
    tjss = []
    reobj = re.compile(r'href="[\d\D]*?</a></td><td>[\d\D]*?</td><td>[\d\D]*?</td><td>([\d\D]*?)</td><td>')
    for match in reobj.finditer(html):
        tjss.append(match.group(1))
    return tjss

def _get_tgl(html):
    '''爬取该网页通过率'''
    tgls = []
    reobj = re.compile(r'href="[\d\D]*?</a></td><td>[\d\D]*?</td><td>[\d\D]*?</td><td>[\d\D]*?</td><td>([\d\D]*?)</td></tr>')
    for match in reobj.finditer(html):
        tgls.append(match.group(1))
    return tgls

def _get_xqylj(html):
    '''爬取该网页题目详情页链接'''
    xqyljs = []
    reobj = re.compile(r'<td><a href="([\d\D]*?)" class="">')
    for match in reobj.finditer(html):
        xqyljs.append(match.group(1))
    return xqyljs

@db_session
def task2():
    '''将爬取到的标号，题型，标题，分数，通过数，提交数，通过率，详情页链接入库'''
    for url in _get_url():
        html = _get_html(url)
        for i in range(len(_get_bh(html))):
            s = Tm(bh = _get_bh(html)[i],tx = _get_tx(html),bt = _get_bt(html)[i],fs = _get_fs(html)[i],tgs = _get_tgs(html)[i],tjs = _get_tjs(html)[i],tgl = _get_tgl(html)[i],xqylj = _get_xqylj(html)[i])
            db.commit()

def _get_html2(href):
    '''获取该网页题目链接html'''
    driver = webdriver.Chrome()
    url = 'http://pintia.cn' + href
    driver.get(url)
    time.sleep(5)
    html2 = driver.page_source
    driver.quit()
    return html2

def task3():
    '''将获取的题目链接html入库'''
    with db_session:
        for s in Tm.select():
            s.html = _get_html2(s.xqylj)
            db.commit()

def _get_tmnl(html):
    '''爬取该网页题目内容'''
    html3 = etree.HTML(html,etree.HTMLParser())
    tmnl = html3.xpath('//*[@id="sparkling-daydream"]/div[3]/div[3]/div/div[4]/div[2]/div[1]/div/p[1]//text()')
    return tmnl

def task4():
    '''将爬取的题目内容入库'''
    with db_session:
        for s in Tm.select():
            html = s.html
            if _get_tmnl(html) != []:
                s.tmnl = _get_tmnl(s.html)[0]
                db.commit()

# 对数据库处理
task1()
# 将爬取到的标号，题型，标题，分数，通过数，提交数，通过率，详情页链接入库
task2()
# 将获取的题目链接html入库
task3()
# 将爬取的题目内容入库
task4()