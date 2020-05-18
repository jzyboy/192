#!/usr/bin/env python
# coding: utf-8

# 语雀题目链接：https://www.yuque.com/ol1q37/gi94xp/gpb4iy
# Pony链接：https://editor.ponyorm.com/user/peiban/star/designer
# 数据库链接：https://pan.baidu.com/s/1iixydAjnYb13knp871PU6A    提取码：x5ke

from pony.orm import *
from selenium import webdriver
import time
import requests,re,os

# 建立数据库
db = Database()
class Star(db.Entity):
    id = PrimaryKey(int, column='id', auto=True)
    name = Optional(str, column='name')
    gender = Optional(str, column='gender')
    href = Optional(str, column='href')
    year = Optional(int, column='year')
    month = Optional(int, column='month')
    day = Optional(int, column='day')
    xz = Optional(str, column='xz')
    html = Optional(str, column='html')
    address = Optional(str, column='address')
    height = Optional(float, column='height')
    picture = Optional(str)

def task1():
    '''对数据库的处理'''
    # 在指定路径下创建名为star.sqlite的数据库
    dbpath = r'E:\python\star.sqlite'
    # 如果该数据库在此路径下存在则将原来的数据库删除创建新的数据库
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath,'w')
    f.close()
    # 将声明的实体附加到特定数据库
    db.bind(provider = 'sqlite', filename = 'e:/python/star.sqlite')
    # 实体映射到数据库
    db.generate_mapping(create_tables = True)
    # 打开调试模式
    set_sql_debug(True)

@db_session
def _get_name(html):
    '''爬取明星网页name的信息'''
    names = []
    reobj = re.compile(r'<p class="c-gap-top-small"><a href="[\d\D]*?" title="(.{1,20})" target="_blank">[\d\D]*?</a></p>')
    for match in reobj.finditer(html):
        names.append(match.group(1))
    return names

@db_session
def _get_href(html):
    '''爬取明星网页href的信息'''
    hrefs = []
    reobj = re.compile(r'<p class="c-gap-top-small"><a href="([\d\D]*?)" title=".{1,20}" target="_blank">[\d\D]*?</a></p>')
    for match in reobj.finditer(html):
        hrefs.append("https://www.baidu.com" + match.group(1))
    return hrefs

@db_session
def _get_picture(html):
    '''爬取明星网页图片链接的信息'''
    pictures = []
    reobj = re.compile(r'src="(https://dss)([\d\D]*?)"></a></p>', re.DOTALL)
    for match in reobj.finditer(html):
        pictures.append(match.group(1) + match.group(2))
    return pictures

@db_session
def task2():
    '''打开明星网页，点击女，内地,判断是否为最后一页，如果不是则对name，href，图片的数据采集并存储到列表中，若是最后一页则退出'''
    driver = webdriver.Chrome()
    url = 'https://www.baidu.com/s?wd=%E6%98%8E%E6%98%9F&rsv_spt=1&rsv_iqid=0xbe4b76860031fb66&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=&tn=baiduhome_pg&ch=&rsv_enter=1&rsv_dl=ib&inputT=2978'
    driver.get(url)

    # 点击女，内地
    driver.find_element_by_xpath("//div[@id='1']/div/div/div/div[2]/p/span[4]").click()
    time.sleep(1)
    driver.find_element_by_xpath("//div[@id='1']/div/div/div/div[2]/p[2]/span[3]").click()
    time.sleep(1)

    while True:
        html = driver.page_source
        x = ''
        reobj2 = re.compile(r'<span class="opui-page-next OP_LOG_BTN" style="([\d\D]*?)">下一页</span>')
        for match2 in reobj2.finditer(html):
            x = match2.group(1)
        #判断不是最后一页，对name，href的数据采集并存储到列表中
        if len(x) <= 0:
            for i in range(len(_get_name(html))):
                names = _get_name(html)
                hrefs = _get_href(html)
                pictures = _get_picture(html)
                s = Star(name = names[i] ,gender = "女",href = hrefs[i],picture = pictures[i])
                db.commit()
            # 点击下一页
            driver.find_element_by_xpath("//div[@id='1']/div/div/div[2]/div[2]/p/span[6]").click()
            time.sleep(1)
        #若是最后一页关闭浏览器并退出循环
        else:
            driver.quit()
            break

@db_session
def _get_html(name):
    '''爬取明星百科网页HTML的信息'''
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    url = 'https://baike.baidu.com/item/' + name
    r = requests.get(url,headers = head)
    r.encoding = 'utf-8'
    htmls = r.text
    reobj = re.compile(r'<li class="list-dot list-dot-paddingleft"><div class="para" label-module="para"><a target=["]?_blank["]? href="[\d\D]*?" data-lemmaid="([\d\D]*?)">[\d\D]*?</a></div></li><li class="list-dot list-dot-', re.DOTALL)
    for match in reobj.finditer(htmls):
        url = 'https://baike.baidu.com/item/' + name + '/' + match.group(1)
        r = requests.get(url,headers = head)
        r.encoding = 'utf-8'
        htmls = r.text
        break
    return htmls

@db_session
def _get_xz(html):
    '''爬取明星星座的信息'''
    xzs = ''
    a = ''
    reobj = re.compile(r"""星&nbsp;&nbsp;&nbsp;&nbsp;座</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""")
    for match in reobj.finditer(html):
        a = match.group(1)
        if '<a target=' in a:
            xzs = re.split('>',a)[1].replace('</a','')
        elif len(a) == 2:
            xzs = a
        else:
            xzs = a[:3]
    return xzs

@db_session
def _get_height(html):
    '''爬取明星身高的信息'''
    heights = 0
    a = ''
    reobj = re.compile(r"""身&nbsp;&nbsp;&nbsp;&nbsp;高</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""", re.DOTALL)
    for match in reobj.finditer(html):
        a = match.group(1).replace('&nbsp;','')
        if '.' in a:
            if a[1] == '.' and len(a) > 4 and len(a) < 14:
                heights = float(a[:4]) * 100
            elif a[1] == '.' and len(a) < 5:
                heights = float(a[:3]) * 100
            elif a[3] == '.':
                heights = a[:5]
            else:
                heights = a[:3]
        elif '米' in a and a[1] == '米':
            heights = a.replace('米','')
        elif '尺' in a and a[1] == '尺':
            heights = int(re.split('尺',a)[0]) * 30.5 + int(re.split('尺',a)[1][0]) * 2.54
        elif '呎' in a and a[1] == '呎':
            heights = int(re.split('呎',a)[0]) * 30.5 + int(re.split('呎',a)[1][0]) * 2.54
        elif '微型化' in a:
            pass
        elif str(a[:3]).isdigit() == True:
            heights = a[:3]
        if heights != 0:
            return heights

@db_session
def _get_address(html):
    '''爬取明星出生地的信息'''
    addresss = ''
    a = ''
    reobj = re.compile(r"""出生地</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""")
    for match in reobj.finditer(html):
        a = match.group(1)
        if '<' in a:
            if a.count('<a target=') == 4:
                addresss = re.split('>',a)[1].replace('</a','') + re.split('>',a)[3].replace('</a','') + re.split('>',a)[5].replace('</a','') + re.split('>',a)[7].replace('</a','')
            if a.count('<a target=') == 3:
                addresss = re.split('>',a)[1].replace('</a','') + re.split('>',a)[3].replace('</a','') + re.split('>',a)[5].replace('</a','')
            elif a.count('<a target=') == 2:
                addresss = re.split('>',a)[1].replace('</a','') + re.split('>',a)[3].replace('</a','')
            elif a.count('<a target=') == 1:
                addresss = re.split('>',a)[1].replace('</a','')
            else:
                addresss = re.split('<',a)[0]
        else:
            addresss = a
    #去掉获取到的身高中的"&nbsp;"
    addresss = addresss.replace('&nbsp;','')
    return addresss

@db_session
def _get_year(html):
    '''爬取明星出生年的信息'''
    years = 0
    a = ''
    # sz用于后面将中文数字变成阿拉伯数字
    sz = "一二三四五六七八九"
    # y用于下面存放将中文数字变成阿拉伯数字后的结果
    y = ""
    reobj = re.compile(r'''出生[日期]*?</dt>
<dd class="basicInfo-item value[\d\D]*?">
([\d\D]*?)
</dd>''', re.DOTALL)
    for match in reobj.finditer(html):
        a = match.group(1)
        if str(a[:4]).isdigit() == True:
            years = a[:4]
        elif re.split('年',match.group(1))[0][-4:].isdigit() == True:
            years = re.split('年',a)[0][-4:]
        elif re.split('年',a)[0][-4:] == '</a>' and re.split('年',a)[0][-8:-4].isdigit() == True:
            years = re.split('年',a)[0][-8:-4]
        if years != 0:
            return years

@db_session
def _get_month(html):
    '''爬取明星出生月的信息'''
    months = 0
    a = ''
    reobj = re.compile(r'''出生[日期]*?</dt>
<dd class="basicInfo-item value[\d\D]*?">
([\d\D]*?)
</dd>''', re.DOTALL)
    for match in reobj.finditer(html):
        a = match.group(1)
        if '月' in a:
            if str(re.split('月',a)[0][-2:]).isdigit() == True:
                months = re.split('月',a)[0][-2:]
            elif str(re.split('月',a)[0][-1:]).isdigit() == True:
                months = re.split('月',a)[0][-1:]
            elif '</a>'in re.split('月',a)[0]:
                if str(re.split('月',a)[0][-6:-4]).isdigit() == True:
                    months = re.split('月',a)[0][-6:-4]
                if str(re.split('月',a)[0][-5:-4]).isdigit() == True:
                    months = re.split('月',a)[0][-5:-4]
        elif  '/' in a and str(re.split('/',a)[1]).isdigit() == True and len(a)>5:
            months = re.split('/',a)[1]
        elif  '-' in a and str(re.split('-',a)[1]).isdigit() == True and len(a)>5:
            months = re.split('-',a)[1]
        elif  ' - ' in a and str(re.split(' - ',a)[1]).isdigit() == True and len(a)>5: 
            months = re.split(' - ',match.group(1))[1]
        elif  '，' in a and str(re.split('，',a)[1]).isdigit() == True and len(a)>5:
            months = re.split('，',match.group(1))[1]
        elif  '－' in a and str(re.split('－',a)[1]).isdigit() == True and len(a)>5:
            months = re.split('－',a)[1]
        elif '.' in a and str(a.split('.')[1]).isdigit() == True and len(a)>5:
            months = match.group(1).split('.')[1]
        elif '年' not in a and len(a) <6 and str(a).isdigit() != True:
            if str(a[:2]).isdigit() == True:
                months = a[:2]
            elif str(a[:1]).isdigit() == True:
                months = a[:1]
        elif '年' in a:
            if str(re.split('年',a)[1][:2]).isdigit() == True:
                months = re.split('年',a)[1][:2]
            elif str(re.split('年',a)[1][:1]).isdigit() == True:
                months = re.split('年',a)[1][:1]
        if months != 0:
            return months

@db_session
def _get_day(html):
    '''爬取明星出生日的信息'''
    days = 0
    reobj = re.compile(r"""出生日期</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""", re.DOTALL)
    for match in reobj.finditer(html):
        a = match.group(1)
        if str(a).isdigit() != True and str(a[-2:]).isdigit() == True:
            days = match.group(1)[-2:]
        elif str(a).isdigit() != True and str(a[-1:]).isdigit() == True:
            days = a[-1:]
        elif a[-1:] == '号' and a[-3:-1].isdigit() == True:
            days = a[-3:-1]
        elif a[-1:] == '号' and a[-2:-1].isdigit() == True:
            days = a[-2:-1]
        elif '日' in a and str(a[-3:-1]).strip().isdigit() == True:
            days = str(a[-3:-1]).strip()
        elif '日' in a and str(a[-2:-1]).strip().isdigit() == True:
            days = a[-2:-1].strip()
        elif a[-5:-1] == '</a>':
            if str(a[-7:-5]).strip().isdigit() == True:
                days = a[-7:-5]
            elif str(a[-6:-5]).strip().isdigit() == True:
                days = a[-6:-5]
        elif '月' in a and str(re.split('月',a)[1][:2]).strip().isdigit() == True:
            days = re.split('月',a)[1][:2].strip()
        elif '月' in a and str(re.split('月',a)[1][:1]).strip().isdigit() == True:
            days = re.split('月',a)[1][:1].strip()
        elif '日' in a and a[-1:] == '日' and str(a[-3:-1]).strip().isdigit() == True:
            days = a[-3:-1].strip()
        elif '-' in a and str(re.split('-',a)[1][:2]).strip().isdigit() == True:
            if len(a) < 5:
                days = re.split('-',a)[1][:2].strip()
            elif str(re.split('-',a)[2][:2]).strip().isdigit() == True:
                days = re.split('-',a)[2][:2].strip()
        elif '-' in a and len(a)< 5 and str(re.split('-',a)[1][:1]).strip().isdigit() == True:
            days = re.split('-',a)[1][:1].strip()
        if days != 0:
            return days

def task3():
    '''将爬取到的数据入库'''
    with db_session:
        for s in Star.select():
            # 将爬取到的明星的HTML入库
            s.html = _get_html(s.name)
            # 将爬取到的明星的星座入库
            s.xz = _get_xz(s.html)
            # 将爬取到的明星的身高入库
            s.height = _get_height(s.html)
            # 将爬取到的明星的出生地入库
            s.address = _get_address(s.html)
            # 将爬取到的明星的出生年入库
            s.year = _get_year(s.html)
            # 将爬取到的明星的出生月入库
            s.month = _get_month(s.html)
            # 将爬取到的明星的出生日入库
            s.day = _get_day(s.html)
            db.commit()

# 数据库处理
task1()
# 打开明星网页，点击女，内地,判断是否为最后一页，如果不是则对name，href，图片的数据采集并存储到列表中，若是最后一页则退出
task2()
# 将爬取到的数据入库
task3()