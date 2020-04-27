#!/usr/bin/env python
# coding: utf-8

# 语雀题目链接：https://www.yuque.com/ol1q37/gi94xp/vy59wr
# Pony链接：https://editor.ponyorm.com/user/peiban/Tm/designer

from pony.orm import *
import requests,time,re,os
from selenium import webdriver
from lxml import etree

# 初始值
bts = []
fss = []
tgss = []
tjss = []
tgls = []
xqyljs = []

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

@db_session
def task2():
    '''获取网页源代码将该网页下爬取到的部分数据入库'''
    driver = webdriver.Chrome()
    url = 'https://pintia.cn/problem-sets/1111652100718116864/problems/type/7'
    driver.get(url)
    time.sleep(1)
    for i in range(2):
        if i == 0:
            html = driver.page_source
            # 将爬取到的编程题的标号、题型写入数据库，并将标题、分数、通过数、提交数、通过率、详情页链接放入对应list
            _get_bh(html)
            _get_tx(html)
            _get_bt(html)
            _get_fs(html)
            _get_tgs(html)
            _get_tjs(html)
            _get_tgl(html)
            _get_xqylj(html)
        else:
            driver.find_element_by_xpath("//div[@id='sparkling-daydream']/div[3]/div[3]/div/ul/li/a/div/div[2]").click()
            time.sleep(1)
            html = driver.page_source
            # 将爬取到的函数题的标号、题型写入数据库，并将对应list里的所有题目入库
            _get_bh(html)
            _get_tx(html)
            for s in Tm.select():
                s.bt = _get_bt(html)[s.id - 1]
                s.fs = _get_fs(html)[s.id - 1]
                s.tgs = _get_tgs(html)[s.id - 1]
                s.tjs = _get_tjs(html)[s.id - 1]
                s.tgl = _get_tgl(html)[s.id - 1]
                s.xqylj = _get_xqylj(html)[s.id - 1]
                db.commit()

@db_session
def _get_bh(html):
    '''爬取该网页题目标号'''
    reobj = re.compile(r'<tr><td class="answerIcon_1du7d"></td><td>([\d\D]*?)</td><td><a href=[\d\D]*?')
    for match in reobj.finditer(html):
        s = Tm(bh = match.group(1))
        db.commit()

@db_session
def _get_tx(html):
    '''爬取该网页题型并入库'''
    for s in Tm.select():
        if '函数' in s.bh:
            s.tx = "函数题"
        else:
            s.tx = "编程题"
        db.commit()

@db_session
def _get_bt(html):
    '''爬取该网页标题'''
    reobj = re.compile(r'<td><a href="[\d\D]*?class="">([\d\D]*?)</a></td>')
    for match in reobj.finditer(html):
        bts.append(match.group(1))
    return bts

@db_session
def _get_fs(html):
    '''爬取该网页分数'''
    reobj = re.compile(r'class="answerIcon_1du7d"></td><td>[\d\D]*?href="[\d\D]*?</a></td><td>([\d\D]*?)</td><td>')
    for match in reobj.finditer(html):
        fss.append(match.group(1))
    return fss

@db_session
def _get_tgs(html):
    '''爬取该网页通过数'''
    reobj = re.compile(r'class="answerIcon_1du7d"></td><td>[\d\D]*?href="[\d\D]*?</a></td><td>[\d\D]*?</td><td>([\d\D]*?)</td><td>')
    for match in reobj.finditer(html):
        tgss.append(match.group(1))
    return tgss

@db_session
def _get_tjs(html):
    '''爬取该网页提交数'''
    reobj = re.compile(r'href="[\d\D]*?</a></td><td>[\d\D]*?</td><td>[\d\D]*?</td><td>([\d\D]*?)</td><td>')
    for match in reobj.finditer(html):
        tjss.append(match.group(1))
    return tjss

@db_session
def _get_tgl(html):
    '''爬取该网页通过率'''
    reobj = re.compile(r'href="[\d\D]*?</a></td><td>[\d\D]*?</td><td>[\d\D]*?</td><td>[\d\D]*?</td><td>([\d\D]*?)</td></tr>')
    for match in reobj.finditer(html):
        tgls.append(match.group(1))
    return tgls

@db_session
def _get_xqylj(html):
    '''爬取该网页题目详情页链接'''
    reobj = re.compile(r'<td><a href="([\d\D]*?)" class="">')
    for match in reobj.finditer(html):
        xqyljs.append(match.group(1))
    return xqyljs

@db_session
def _get_html(href):
    '''获取该网页题目链接html'''
    driver = webdriver.Chrome()
    url = 'http://pintia.cn' + href
    driver.get(url)
    time.sleep(1)
    html = driver.page_source
    driver.quit()
    return html

def task3():
    '''将获取的题目链接html入库'''
    with db_session:
        for s in Tm.select():
            s.html = _get_html(s.xqylj)
            db.commit()

@db_session
def _get_tmnl(html):
    '''爬取该网页题目链接题目内容'''
    html2 = etree.HTML(html,etree.HTMLParser())
    tmnl = html2.xpath('//*[@id="sparkling-daydream"]/div[3]/div[3]/div/div[4]/div[2]/div[1]/div/p[1]//text()')
    return tmnl

def task4():
    '''将爬取的题目内容入库'''
    with db_session:
        for s in Tm.select():
            html = s.html
            if _get_tmnl(html) != []:
                s.tmnl = _get_tmnl(s.html)[0]
                db.commit()

task1()
task2()
task3()
task4()