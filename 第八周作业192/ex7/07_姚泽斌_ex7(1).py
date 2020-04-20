#!/usr/bin/env python
# coding: utf-8

# 语雀题目链接：https://www.yuque.com/ol1q37/gi94xp/gpb4iy
from pony.orm import *
from selenium import webdriver
import time
import requests,re,os

# Pony链接：https://editor.ponyorm.com/user/peiban/star/designer

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


def create_database():
    dbpath = 'e:/python/star.sqlite'
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath,"w")
    f.close()

    # 将声明的实体附加到特定数据库
    db.bind(provider = 'sqlite', filename = dbpath)
    # 实体映射到数据库
    db.generate_mapping(create_tables = True)
    # 打开调试模式
    set_sql_debug(True)

# 爬取明星网页的name,并入库，顺表将固定值女入库
@db_session
def _get_name(html):
    names = []
    reobj = re.compile(r'<p class="c-gap-top-small"><a href="[\d\D]*?" title="(.{1,20})" target="_blank">[\d\D]*?</a></p>')
    for match in reobj.finditer(html):
        names.append(match.group(1))
    return names

# 爬取明星网页的href
@db_session
def _get_href(html):
    hrefs = []
    reobj = re.compile(r'<p class="c-gap-top-small"><a href="([\d\D]*?)" title=".{1,20}" target="_blank">[\d\D]*?</a></p>')
    for match in reobj.finditer(html):
        hrefs.append("https://www.baidu.com" + match.group(1))
    return hrefs

# 爬取明星网页的图片链接
@db_session
def get_picture(html):
    pictures = []
    reobj = re.compile(r'src="(https://dss)([\d\D]*?)"></a></p>', re.DOTALL)
    for match in reobj.finditer(html):
        pictures.append(match.group(1) + match.group(2))
    return pictures
    
    
# 打开明星网页，点击女，内地,判断是否为最后一页，如果不是则对name，href，图片的数据采集并存储到列表中，若是最后一页则退出
@db_session
def task1():
    # 打开明星网页
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
            for i in range(len(get_name(html))):
                names = get_name(html)
                hrefs = get_href(html)
                pictures = get_picture(html)
                s = Star(name = names[i] ,gender = "女",href = hrefs[i],picture = pictures[i])
                db.commit()
            # 点击下一页
            driver.find_element_by_xpath("//div[@id='1']/div/div/div[2]/div[2]/p/span[6]").click()
            time.sleep(1)
        #若是最后一页关闭浏览器并退出循环
        else:
            driver.quit()
            break

# 爬取明星百科网页的HTML
@db_session
def get_html(name):
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

# 爬取明星的星座
@db_session
def get_xz(html):
    xzs = ''
    reobj = re.compile(r"""星&nbsp;&nbsp;&nbsp;&nbsp;座</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""")
    for match in reobj.finditer(html):
        if '<a target=' in match.group(1):
            xzs = re.split('>',match.group(1))[1].replace('</a','')
        elif len(match.group(1)) == 2:
            xzs = match.group(1)
        else:
            xzs = match.group(1)[:3]
    return xzs

# 爬取明星的身高
@db_session
def get_height(html):
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

# 爬取明星的出生地
@db_session
def get_address(html):
    addresss = ''
    reobj = re.compile(r"""出生地</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""")
    for match in reobj.finditer(html):
        if '<' in match.group(1):
            if match.group(1).count('<a target=') == 4:
                addresss = re.split('>',match.group(1))[1].replace('</a','') + re.split('>',match.group(1))[3].replace('</a','') + re.split('>',match.group(1))[5].replace('</a','') + re.split('>',match.group(1))[7].replace('</a','')
            if match.group(1).count('<a target=') == 3:
                addresss = re.split('>',match.group(1))[1].replace('</a','') + re.split('>',match.group(1))[3].replace('</a','') + re.split('>',match.group(1))[5].replace('</a','')
            elif match.group(1).count('<a target=') == 2:
                addresss = re.split('>',match.group(1))[1].replace('</a','') + re.split('>',match.group(1))[3].replace('</a','')
            elif match.group(1).count('<a target=') == 1:
                addresss = re.split('>',match.group(1))[1].replace('</a','')
            else:
                addresss = re.split('<',match.group(1))[0]
        else:
            addresss = match.group(1)
    #去掉获取到的身高中的"&nbsp;"
    addresss = addresss.replace('&nbsp;','')
    return addresss

# 爬取明星的出生年
@db_session
def get_year(html):
    # sz用于后面将中文数字变成阿拉伯数字
    sz = "一二三四五六七八九"
    years = 0
    # y用于下面存放将中文数字变成阿拉伯数字后的结果
    y = ""
    reobj = re.compile(r"""出生[日期]*?</dt>
<dd class="basicInfo-item value[\d\D]*?">
([\d\D]*?)
</dd>""", re.DOTALL)
    for match in reobj.finditer(html):
        if str(match.group(1)[:4]).isdigit() == True:
            years = match.group(1)[:4]
        elif re.split('年',match.group(1))[0][-4:].isdigit() == True:
            years = re.split('年',match.group(1))[0][-4:]
        elif re.split('年',match.group(1))[0][-4:] == '</a>' and re.split('年',match.group(1))[0][-8:-4].isdigit() == True:
            years = re.split('年',match.group(1))[0][-8:-4]
        if years != 0:
            return years

# 爬取明星的出生月
@db_session
def _get_month(html):
    months = 0
    reobj = re.compile(r"""出生[日期]*?</dt>
<dd class="basicInfo-item value[\d\D]*?">
([\d\D]*?)
</dd>""", re.DOTALL)
    for match in reobj.finditer(html):
        if '月' in match.group(1):
            if str(re.split('月',match.group(1))[0][-2:]).isdigit() == True:
                months = re.split('月',match.group(1))[0][-2:]
            elif str(re.split('月',match.group(1))[0][-1:]).isdigit() == True:
                months = re.split('月',match.group(1))[0][-1:]
            elif '</a>'in re.split('月',match.group(1))[0]:
                if str(re.split('月',match.group(1))[0][-6:-4]).isdigit() == True:
                    months = re.split('月',match.group(1))[0][-6:-4]
                if str(re.split('月',match.group(1))[0][-5:-4]).isdigit() == True:
                    months = re.split('月',match.group(1))[0][-5:-4]
        elif  '/' in match.group(1) and str(re.split('/',match.group(1))[1]).isdigit() == True and len(match.group(1))>5:
            months = re.split('/',match.group(1))[1]
        elif  '-' in match.group(1) and str(re.split('-',match.group(1))[1]).isdigit() == True and len(match.group(1))>5:
            months = re.split('-',match.group(1))[1]
        elif  ' - ' in match.group(1) and str(re.split(' - ',match.group(1))[1]).isdigit() == True and len(match.group(1))>5: 
            months = re.split(' - ',match.group(1))[1]
        elif  '，' in match.group(1) and str(re.split('，',match.group(1))[1]).isdigit() == True and len(match.group(1))>5:
            months = re.split('，',match.group(1))[1]
        elif  '－' in match.group(1) and str(re.split('－',match.group(1))[1]).isdigit() == True and len(match.group(1))>5:
            months = re.split('－',match.group(1))[1]
        elif '.' in match.group(1) and str(match.group(1).split('.')[1]).isdigit() == True and len(match.group(1))>5:
            months = match.group(1).split('.')[1]
        elif '年' not in match.group(1) and len(match.group(1)) <6 and str(match.group(1)).isdigit() != True:
            if str(match.group(1)[:2]).isdigit() == True:
                months = match.group(1)[:2]
            elif str(match.group(1)[:1]).isdigit() == True:
                months = match.group(1)[:1]
        elif '年' in match.group(1):
            if str(re.split('年',match.group(1))[1][:2]).isdigit() == True:
                months = re.split('年',match.group(1))[1][:2]
            elif str(re.split('年',match.group(1))[1][:1]).isdigit() == True:
                months = re.split('年',match.group(1))[1][:1]
        if months != 0:
            return months

# 爬取明星的出生日
@db_session
def _get_day(html):
    days = 0
    reobj = re.compile(r"""出生日期</dt>
<dd class="basicInfo-item value">
([\d\D]*?)
</dd>""", re.DOTALL)
    for match in reobj.finditer(html):
        if str(match.group(1)).isdigit() != True and str(match.group(1)[-2:]).isdigit() == True:
            days = match.group(1)[-2:]
        elif str(match.group(1)).isdigit() != True and str(match.group(1)[-1:]).isdigit() == True:
            days = match.group(1)[-1:]
        elif match.group(1)[-1:] == '号' and match.group(1)[-3:-1].isdigit() == True:
            days = match.group(1)[-3:-1]
        elif match.group(1)[-1:] == '号' and match.group(1)[-2:-1].isdigit() == True:
            days = match.group(1)[-2:-1]
        elif '日' in match.group(1) and str(match.group(1)[-3:-1]).strip().isdigit() == True:
            days = str(match.group(1)[-3:-1]).strip()
        elif '日' in match.group(1) and str(match.group(1)[-2:-1]).strip().isdigit() == True:
            days = match.group(1)[-2:-1].strip()
        elif match.group(1)[-5:-1] == '</a>':
            if str(match.group(1)[-7:-5]).strip().isdigit() == True:
                days = match.group(1)[-7:-5]
            elif str(match.group(1)[-6:-5]).strip().isdigit() == True:
                days = match.group(1)[-6:-5]
        elif '月' in match.group(1) and str(re.split('月',match.group(1))[1][:2]).strip().isdigit() == True:
            days = re.split('月',match.group(1))[1][:2].strip()
        elif '月' in match.group(1) and str(re.split('月',match.group(1))[1][:1]).strip().isdigit() == True:
            days = re.split('月',match.group(1))[1][:1].strip()
        elif '日' in match.group(1) and match.group(1)[-1:] == '日' and str(match.group(1)[-3:-1]).strip().isdigit() == True:
            days = match.group(1)[-3:-1].strip()
        elif '-' in match.group(1) and str(re.split('-',match.group(1))[1][:2]).strip().isdigit() == True:
            if len(match.group(1)) < 5:
                days = re.split('-',match.group(1))[1][:2].strip()
            elif str(re.split('-',match.group(1))[2][:2]).strip().isdigit() == True:
                days = re.split('-',match.group(1))[2][:2].strip()
        elif '-' in match.group(1) and len(match.group(1))< 5 and str(re.split('-',match.group(1))[1][:1]).strip().isdigit() == True:
            days = re.split('-',match.group(1))[1][:1].strip()
        if days != 0:
            return days




def info_extract():
# 将爬取到的数据入库
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
            time.sleep(2)
            db.commit()




create_database()
# 打开明星网页，点击女，内地,判断是否为最后一页，如果不是则对name，href，图片的数据采集并存储到列表中，若是最后一页则退出
task1()
info_extract()