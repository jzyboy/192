#encoding=utf-8
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from lxml import etree
import time
import requests, re
from pony.orm import *





class Star(db.Entity):
    id = PrimaryKey(int, auto=True)
    name = Optional(str, column='name')
    gender = Optional(str, column='gender')
    picture = Optional(str, column='picture')
    href = Optional(str, column='href')
    baikehref = Optional(str, column='baikehref')
    year = Optional(int, column='year')
    month = Optional(int, column='month')
    day = Optional(int, column='day')
    xz = Optional(str, column='xz')
    html = Optional(str, column='html')
    address = Optional(str, column='address')
    height = Optional(float, column='height')


def create_database():
    # 生成数据库
    db = Database()
    dbpath = 'e:/python/star.sqlite'
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath,"w")
    f.close()
    db.bind(provider='sqlite', filename=r'C:\Users\Administrator\Desktop\star.sqlite')

    db.generate_mapping(create_tables=True)

    set_sql_debug(True)



@db_session()
def task1():
    '''获取一页的明星名字、明星小图片、链接，导入数据库'''
    html=etree.HTML(driver.page_source,etree.HTMLParser())
    names=html.xpath('//*[@id="1"]/div/div[1]/div[2]/div[1]/div/p[2]/a/text()')#获取这一页明星名字
    pictures=html.xpath('//*[@id="1"]/div/div[1]/div[2]/div[1]/div/p[1]/a/img/@src')#获取这一页明星图片
    hrefs=html.xpath('//*[@id="1"]/div/div[1]/div[2]/div[1]/div/p[1]/a/@href')#获取这一页明星链接
    #导入数据库
    for i in range(len(names)):
        s=Star(name = names[i],gender = '女', picture = pictures[i], href = "https://www.baidu.com"+hrefs[i] )
        db.commit()


@db_session()
def task2():
    '''循环调用函数task1获取数据，直到没有下一页'''
    while True:
        try:
            _task1()
            next_btn=wait.until(EC.element_to_be_clickable(
                (By.XPATH,'//*[@id="1"]/div/div[1]/div[2]/div[2]/p/span[6]')))#等待下一页能被点击，没有出现下一页了退出
            next_btn.click()#点击下一页
            time.sleep(1)
        except:
            print('没有下一页了，获取结束')
            driver.close()
            break


@db_session()
def get_html(baike_href):
    '''获取一位明星百科页面的html，保存到库'''
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'}
    r = requests.get(baikehref,headers=head)
    r.encoding = 'utf-8'
    s.baikehref = baikehref
    s.html = r.text
    db.commit()


@db_session()
def get_height(html):
    '''获取一人的身高,保存进数据库，没有身高不用保存'''
    if re.search(r'<dt class="basicInfo-item name">身&nbsp;&nbsp;&nbsp;&nbsp;高</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html):
        height=re.search(r'<dt class="basicInfo-item name">身&nbsp;&nbsp;&nbsp;&nbsp;高</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html).group(1).strip()
        try:
            if ('CM' in height) or ('cm' in height) or ('厘米' in height):
                height=float(height[:-2])
            elif ('M' in height) or ('m' in height) or ('米' in height):
                height=float(height[:-1])*100
            s.height=height
            db.commit()
        except:
            pass


@db_session()
def get_xz(html):
    '''获取一人的星座,保存进数据库，没有星座不用保存'''
    match = re.search(r'<dt class="basicInfo-item name">星&nbsp;&nbsp;&nbsp;&nbsp;座</dt>\n<dd class="basicInfo-item value">\n<a[\d\D]*?>([\d\D]*?)</a',html)
    if match:
        s.xz = match.group(1).strip()
        db.commit()

    elif re.search(r'<dt class="basicInfo-item name">星&nbsp;&nbsp;&nbsp;&nbsp;座</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html):
        xingzuo=re.search(r'<dt class="basicInfo-item name">星&nbsp;&nbsp;&nbsp;&nbsp;座</dt>\n<dd class="basicInfo-item value">([\d\D]*?)</dd',html).group(1).strip()
        s.xz=xingzuo
        db.commit()


@db_session()
def get_address(html):
    '''获取一人的籍贯，保存进数据库，没有则不用保存'''
    if re.search(r'<dt class="basicInfo-item name">出生地</dt>\n<dd class="basicInfo-item value">\n<a [\d\D]*?>([\d\D]*?)</a',html):
        jiguan = re.search(r'<dt class="basicInfo-item name">出生地</dt>\n<dd class="basicInfo-item value">\n<a [\d\D]*?>([\d\D]*?)</a',html).group(1).strip()
        s.address = jiguan
        db.commit()
    elif re.search(r'<dt class="basicInfo-item name">出生地</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html):
        jiguan = re.search(r'<dt class="basicInfo-item name">出生地</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html).group(1).strip()
        s.address = jiguan
        db.commit()


@db_session()
def get_date(html):
    '''获取出生日期，分为年月日保存进数据库，没有则不保存'''
    if re.search(r'<dt class="basicInfo-item name">出生日期</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html):
        birth=re.search(r'<dt class="basicInfo-item name">出生日期</dt>\n<dd class="basicInfo-item value">([\d\D]*?)<',html).group(1).strip()
        if ('年' in birth) and ('月' in birth) and ('日' in birth):
            year,month,day = re.split('[年月日]',birth)[:3]
            try:
                s.year = int(year)
                s.month = int(month)
                s.day = int(day)
                db.commit()
            except:
                pass
        elif ('年' in birth) and ('月' in birth):
            year,month = re.split('[年月]',birth)[:2]
            try:
                s.year = int(year)
                s.month = int(month)
                db.commit()
            except:
                pass
        elif '年' in birth:
            year = re.split('[年]',birth)[0]
            try:
                s.year = int(year)
                db.commit()
            except:
                pass
        elif ('月' in birth) and ('日' in birth):
            month,day = re.split('[月日]',birth)[:2]
            try:
                s.month = int(month)
                s.day = int(day)
                db.commit()
            except:
                pass



def main():
    # 打开网页
    url = 'https://www.baidu.com/s?wd=%E6%98%8E%E6%98%9F&rsv_spt=1&rsv_iqid=0xbe4b76860031fb66&issp=1&f=8&rsv_bp=1&rsv_idx=2&ie=utf-8&rqlang=&tn=baiduhome_pg&ch=&rsv_enter=1&rsv_dl=ib&inputT=2978'
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(2)
    wait = WebDriverWait(driver, 10)
    # 点击内地女
    driver.find_element_by_xpath('//*[@id="1"]/div/div[1]/div[1]/div[2]/p[1]/span[4]').click()
    driver.find_element_by_xpath('//*[@id="1"]/div/div[1]/div[1]/div[2]/p[2]/span[3]').click()

    # 调用函数抓取数据
    # task2()


    # 遍历数据库，构建明星百科url，将所有明星html保存入库
    with db_session:
        for s in Star.select():
            baikehref = 'https://baike.baidu.com/item/' + s.name
            get_html(baikehref)

    # 遍历数据库，抓取需要的数据
    with db_session:
        for s in Star.select():
            get_height(s.html)
            get_xz(s.html)
            get_address(s.html)
            get_date(s.html)

main()
