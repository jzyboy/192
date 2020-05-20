#!/usr/bin/env python
# coding: utf-8

# # 导入模块

# In[3]:


from selenium import webdriver
import os
import time
import re
import requests


# # 创建数据库

# In[4]:


from pony.orm import *


db = Database()


class Ttimu(db.Entity):
    id = PrimaryKey(int, auto=True)
    types = Optional(str,column = 'types')
    tab = Optional(str,column = 'tab')
    href = Optional(str,column = 'url')
    title = Optional(str,column = 'title')
    grade = Optional(int,column = 'fs')
    tgs = Optional(int,column = 'tgs')
    tjs = Optional(int,column = 'tjs')
    tgl = Optional(float,column = 'tgl')
    html = Optional(str,column = 'html')
    content = Optional(str,column = 'content')



# db.generate_mapping()


# In[6]:


def get_create_database():
    dbpath = 'f:/ex8/timuxx.sqlite'
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath,"w")
    f.close()
    db.bind(provider='sqlite',filename='f:/ex8/timuxx.sqlite')
    db.generate_mapping(create_tables=True)
    set_sql_debug(True)


# # 定义获取网页中的题型,标号,题目链接,标题,分数,通过数,提交数,通过率的函数

# In[7]:

@db_session
def get_timudata(html):
    reobj = re.compile(r'<tr>[\d\D]*?<td>([\d\D]*?)</td>[\d\D]*?"([\d\D]*?)" class="">([\d\D]*?)<[\d\D]*?<td>([\d\D]*?)</td><td>([\d\D]*?)</td><td>([\d\D]*?)<[\d\D]*?<td>([\d\D]*?)<')
    for match in reobj.finditer(html):
        if url[-1] == "7":
            tx = "编程题"
        elif url[-1] == "6":
            tx = "函数题"
        bh = match.group(1)
        tmulj = "https://pintia.cn" + match.group(2)
        bt = match.group(3)
        fsu = match.group(4)
        tgsu = match.group(5)
        tjsu = match.group(6)
        tglu = match.group(7)
        s = Ttimu(types = tx,tab = bh,href = tmulj,title = bt,grade = fsu,tgs = tgsu,tjs = tjsu,tgl = tglu)
        db.commit()


# # 定义获取每个题目详情页html代码的函数

# In[8]:

@db_session
def get_html(url):
    driver=webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    h=driver.page_source
    timu.html = h
    db.commit()
    driver.close()

# # 定义获取每个题目内容的函数

# In[9]:

@db_session
def get_content(html):
    if re.search(r'<div>[\d\D]*?<div class="ques-view"><p>([\d\D]*?)</p>', html):
        match = re.search(r'<div>[\d\D]*?<div class="ques-view"><p>([\d\D]*?)</p>', html)
        tmunr = match.group(1).strip()
        timu.content = tmunr
        db.commit()


# # 整体步骤

# In[10]:


get_create_database()


# In[11]:


url = "https://pintia.cn/problem-sets/1111652100718116864/problems/type/7"
driver=webdriver.Chrome()
driver.get(url)
time.sleep(2)
h=driver.page_source
Ttimu.html = h
time.sleep(2)
get_timudata(h)
time.sleep(2)
driver.close()


# In[12]:


url = "https://pintia.cn/problem-sets/1111652100718116864/problems/type/6"
driver=webdriver.Chrome()
driver.get(url)
time.sleep(2)
h=driver.page_source
Ttimu.html = h
time.sleep(2)
get_timudata(h)
driver.close()



# In[13]:

with db_session:
    for timu in Ttimu.select():
        get_html(timu.href)
        get_content(timu.html)


# In[ ]:




