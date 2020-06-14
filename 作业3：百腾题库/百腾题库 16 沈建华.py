# 题目链接  https://www.yuque.com/ol1q37/gi94xp/vy59wr
# pony链接  https://editor.ponyorm.com/user/GioooGzL/two/designer
from selenium import webdriver
from lxml import etree
import time
import os
from pony.orm import *

db = Database()


class Tm(db.Entity):
    id = PrimaryKey(int, auto=True)
    tixing = Optional(str, column='tixing')
    biaohao = Optional(str, column='biaohao')
    biaoti = Optional(str, column='biaoti')
    fengshu = Optional(str, column='fengshu')
    tongguoshu = Optional(str, column='tongguoshu')
    tijiaoshu = Optional(str, column='tijiaoshu')
    tongguolv = Optional(str, column='tongguolv')
    tmneirong = Optional(str, column='tmneirong')
    html = Optional(str, column='html')
    href = Optional(str, column='href')


def create_database():
    """创建数据库"""
    dbpath = r'C:\Users\Admin\timu.sqlite'
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath, 'w')
    f.close()

    db.bind(provider='sqlite', filename=dbpath)

    db.generate_mapping(create_tables=True)

    set_sql_debug(True)


@db_session()
def _get_data(url):
    """
    获取页面题目编号、标题、分数等信息，保存到数据库
    """
    if url[-1] == '6':
        tixing = '函数题'
    else:
        tixing = '编程题'

    driver.get(url)  # 打开网页
    time.sleep(5)
    html = driver.page_source  # 获取html
    # 解析获取所需要的内容
    etr = etree.HTML(html, etree.HTMLParser())
    for tr in etr.xpath('//tbody/tr'):
        biaohao = tr.xpath('td[2]/text()')[0]  # 编号
        biaoti = tr.xpath('td[3]/a/text()')[0]  # 标题
        fengshu = tr.xpath('td[4]/text()')[0]  # 分数
        tongguoshu = tr.xpath('td[5]/text()')[0]  # 通过数
        tijiaoshu = tr.xpath('td[6]/text()')[0]  # 提交数
        tongguolv = tr.xpath('td[7]/text()')[0]  # 通过率
        href = 'https://pintia.cn' + tr.xpath('td[3]/a/@href')[0]  # 链接
        s = Tm(tixing=tixing, biaohao=biaohao, biaoti=biaoti, fengshu=fengshu, tongguoshu=tongguoshu,
               tijiaoshu=tijiaoshu, tongguolv=tongguolv, href=href)
        db.commit()


@db_session()
def get_all_tm():
    """获取所有函数题和编程题"""
    urls = ['https://pintia.cn/problem-sets/1111652100718116864/problems/type/6',
            'https://pintia.cn/problem-sets/1111652100718116864/problems/type/7']
    for url in urls:
        _get_data(url)


def _get_html(url):
    """获取题目详情页的html"""
    driver.get(url)
    time.sleep(2)
    return driver.page_source


@db_session()
def get_all_html():
    """获取全部题目的详情页html,保存进数据库"""
    with db_session:
        for t in Tm.select():
            t.html = _get_html(t.href)
            db.commit()


def _get_tmnr(html):
    """获取题目的内容"""
    etr = etree.HTML(html, etree.HTMLParser())
    tm = etr.xpath('//*[@id="sparkling-daydream"]/div[3]/div[3]/div/div[4]/div[2]/div[1]/div/p[1]//text()')
    s = ''
    try:
        for i in tm:
            s = s + i.strip()
    except:
        s = ''
    return s


@db_session()
def get_all_tmnr():
    """获取所有题目的题目内容,保存进数据库"""
    with db_session:
        for t in Tm.select():
            t.tmneirong = _get_tmnr(t.html)
            db.commit()


if __name__ == '__main__':
    create_database()
    driver = webdriver.Chrome()
    get_all_tm()
    get_all_html()
    get_all_tmnr()
