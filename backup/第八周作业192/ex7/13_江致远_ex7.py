#!/usr/bin/env python
# coding: utf-8

# In[11]:


from selenium import webdriver
import os
import time
import re
import requests


# # 创建数据库

# In[12]:


from pony.orm import *


db = Database()


class Star(db.Entity):
    id = PrimaryKey(int, auto = True)
    name = Optional(str, column = 'name')
    picture = Optional(str, column = 'picture')
    href1 = Optional(str, column = 'href1')
    gender = Optional(str, column = 'gender')
    href = Optional(str, column = 'href')
    year = Optional(int, column = 'year')
    month = Optional(int, column = 'month')
    day = Optional(int, column = 'day')
    xz = Optional(str, column = 'xz')
    html = Optional(str, column = 'html')
    address = Optional(str, column = 'address')
    height = Optional(float, column = 'height')



# db.generate_mapping()


# In[13]:


dbpath = 'f:/ex7/star.sqlite'
if os.path.exists(dbpath):
    os.remove(dbpath)
f = open(dbpath,"w")
f.close()


# In[14]:


db.bind(provider = 'sqlite',filename = 'f:/ex7/star.sqlite')

db.generate_mapping(create_tables = True)

set_sql_debug(True)


# # 定义将名字、链接、小图片，入库的函数

# In[16]:

@db_session
def get_data(h):
    reobj = re.compile(r'<div class="op_exactqa_item c-gap-bottom c-span4 [\d\D]*?"><div class="op_exactqa_feedback OP_LOG_BTN">[\d\D]*?<a href="([\d\D]*?)" title="([\d\D]*?)" target="_blank"><img class="[\d\D]*?" src="([\d\D]*?)">')
    for match in reobj.finditer(h):
        href2 = match.group(1).strip()
        name1 = match.group(2).strip()
        picture1 = match.group(3).strip()
        s = Star(name = name1,href1 = href2,picture = picture1)
        db.commit()


# # 定义获取明星百科链接并入库的函数

# In[ ]:


@db_session
def get_href(n):
    star.href = "https://baike.baidu.com/item/"+n
    db.commit()


# # 定义获取所有详情页链接的源代码并入库的函数

# In[ ]:


@db_session
def get_html(h):
    head = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36'}
    r = requests.get(h,headers = head)
    r.keep_alive = False 
    r.encoding = 'utf-8'
    star.html = r.text
    db.commit()


# # 定义获取明星的星座并入库的函数

# In[ ]:


@db_session
def get_xz(h):
    if re.search(r'座</dt>\n<dd class="basicInfo-item value">\n<a[\d\D]*?">([\d\D]*?)</a',h):
        match = re.search(r'座</dt>\n<dd class="basicInfo-item value">\n<a[\d\D]*?">([\d\D]*?)</a',h)
        xz1 = match.group(1).strip()
        star.xz = xz1
   
        db.commit()
    elif re.search(r'座</dt>\n<dd class="basicInfo-item value">\n([\d\D]*?)\n<',h):
        match = re.search(r'座</dt>\n<dd class="basicInfo-item value">\n([\d\D]*?)\n<',h)
        xz1 = match.group(1).strip()
        star.xz = xz1
        db.commit()


# # 定义获取明星的身高并入库的函数

# In[ ]:


@db_session
def get_height(h):
    if re.search(r'高</dt>\n<dd class="basicInfo-item value">\n([\d\D]*?)\n<',h):
        height = re.search(r'高</dt>\n<dd class="basicInfo-item value">\n([\d\D]*?)\n<',h).group(1).strip()
        try:
            if ("cm" in height) or ("CM" in height) or ("Cm" in height) or ("厘米" in height):
                height = float(height[:-2])
            elif  ("m" in height) or ("M" in height) or ("米" in height):
                height = float(height[:-1])*100
            star.height = height
            db.commit()
        except:
            pass
    elif re.search(r'高</dt>\n<dd class="basicInfo-item value">\n([\d\D]*?)<sup',h):
        height = re.search(r'高</dt>\n<dd class="basicInfo-item value">\n([\d\D]*?)<sup',h).group(1).strip("/n")
        try:
            if ("cm" in height) or ("CM" in height) or ("Cm" in height) or ("厘米" in height):
                height = float(height[:-2])
            elif  ("m" in height) or ("M" in height) or ("米" in height):
                height = float(height[:-1])*100
            star.height = height
            db.commit()
        except:
            pass


# # 定义获取明星的性别并入库的函数

# In[ ]:


@db_session
def get_gender():
    star.gender = "女"
    db.commit()


# # 定义获取明星的籍贯并入库的函数

# In[ ]:


@db_session
def get_address(h):
    if re.search(r'<dt class="basicInfo-item name">出生地[\d\D]*?">([\d\D]*?)<',h):
        match = re.search(r'<dt class="basicInfo-item name">出生地[\d\D]*?">([\d\D]*?)<',h)
        jg1 = match.group(1).strip()
        star.address = jg1
        db.commit()


# # 定义获取明星的出生年，月，日并入库的函数

# In[ ]:


@db_session
def get_birth(h):
    if  re.search(r'<dt class="basicInfo-item name">出生日期[\d\D]*?">([\d\D]*?)</dd>',h):
        birth = re.search(r'<dt class="basicInfo-item name">出生日期[\d\D]*?">([\d\D]*?)</dd>',h).group(1).strip()
        if "年" in birth and "月" in birth and "日" in birth: 
            year,month,day = re.split("[年月日]",birth)[:3]
            try:
                star.year = int(year)
                star.month = int(month)
                star.day = int(day)
                db.commit
            except:
                pass
        elif "年" in birth and "月" in birth:
            year,month = re.split("[年月]",birth)[:2]
            try:
                star.year = int(year)
                star.month = int(month)
                db.commit
            except:
                pass
        elif "年" in birth:
            year = re.split("[年]",birth)[:1]
            try:
                star.year = int(year)
                db.commit
            except:
                pass
        elif "月" in birth and "日" in birth: 
            month,day = re.split("[月日]",birth)[:2]
            try:
                star.month = int(month)
                star.day = int(day)
                db.commit
            except:
                pass
        

# # 整体步骤

# In[17]:


driver=webdriver.Chrome()
url = 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=1&rsv_idx=2&tn=baiduhome_pg&wd=%E6%98%8E%E6%98%9F&rsv_spt=1&oq=%25E6%2598%258E%25E6%2598%259F&rsv_pq=a1a2cf770002ec2f&rsv_t=0e3baM8Xu8qPUVhj0snvRVkEdX1Le%2Bm%2FZvXgmFXh1EnnOrdvEFvLRImf6oviVMQdrqmk&rqlang=cn&rsv_enter=0&rsv_dl=tb'
driver.get(url)
time.sleep(1)
driver.find_element_by_xpath("//div[@id='1']/div/div/div/div[2]/p/span[4]").click()
time.sleep(1)
driver.find_element_by_xpath("//div[@id='1']/div/div/div/div[2]/p[2]/span[3]").click()


# In[ ]:

requests.adapters.DEFAULT_RETRIES = 5 
while True:
    html = driver.page_source
    get_data(html)
    with db_session:
        for star in Star.select():
            get_href(star.name)
    match = re.search(r'<span class="opui-page-next OP_LOG_BTN" style="([\d\D]*?)">[\d\D]*?</span>', html)
    if match.group(1) != "display: none;":
        driver.find_element_by_xpath("//div[@id='1']/div/div/div[2]/div[2]/p/span[6]").click()
        time.sleep(1)
    else:
        break
with db_session:
        for star in Star.select():
            get_html(star.href)
            get_xz(star.html)
            get_height(star.html)
            get_gender()
            get_address(star.html)
            get_birth(star.html)

