#!/usr/bin/env python
# coding: utf-8

# 语雀链接：https://www.yuque.com/ol1q37/gi94xp/qgdu4c
# Pony链接：https://editor.ponyorm.com/user/peiban/Py/designer
# 文本链接：https://pan.baidu.com/s/1jmij2dqwSpMyJmgyTjF11Q 提取码：6oyk
# 数据库链接：https://pan.baidu.com/s/1sN6U_uMnGAvnwdQxcsaHtQ 提取码：mkgu 

from pony.orm import *
from selenium import webdriver
import time,os,re,codecs

db = Database()
class Py(db.Entity):
    id = PrimaryKey(int, auto=True)
    hz = Optional(str)
    py1 = Optional(str)
    py1_herf = Optional(str)
    py2 = Optional(str)
    py2_herf = Optional(str)
    py3 = Optional(str)
    py3_herf = Optional(str)
    py4 = Optional(str)
    py4_herf = Optional(str)
    py5 = Optional(str)
    py5_herf = Optional(str)
    py6 = Optional(str)
    py6_herf = Optional(str)

def task1():
    '''对数据库的处理'''
    # 在指定路径下创建名为star.sqlite的数据库
    dbpath = r'E:\python/py.sqlite'
    # 如果该数据库在此路径下存在则将原来的数据库删除创建新的数据库
    if os.path.exists(dbpath):
        os.remove(dbpath)
    f = open(dbpath,'w')
    f.close()
    db.bind(provider = 'sqlite', filename = 'E:/python/py.sqlite')
    db.generate_mapping(create_tables = True)
    set_sql_debug(True)

def _get_option():
    '''配置chrome属性的类'''
    option = webdriver.ChromeOptions()

def _get_drive():
    '''配置参数'''
    option = _get_option()
    drive = webdriver.Chrome(options = option)
    return drive

def _get_py(html):
    py = []
    reobj = re.compile(r'class="op_exactqa_detail_word_pronounce">\[([\d\D]*?)\]</span>')
    for match in reobj.finditer(html):
        py.append(match.group(1))
    return py

def _get_fy(html):
    fy = []
    reobj = re.compile(r'url="([\d\D]*?)" href="javascript:;" onclick="return false;" hidefocus="true"></a>')
    for match in reobj.finditer(html):
        fy.append(match.group(1))
    return fy

def _get_sl(html):
    a = 'href="javascript:;" onclick="return false;" hidefocus="true">'
    b = html.count(a)
    return b

def _get_py1(html,one):
    if _get_sl(html) == 1:
        s = Py(hz = one,py1 = _get_py(html)[0],py1_herf = _get_fy(html)[0])

def _get_py2(html,one):
    if _get_sl(html) == 2:
        s = Py(hz = one,py1 = _get_py(html)[0],py1_herf = _get_fy(html)[0],py2 = _get_py(html)[1],py2_herf =_get_fy(html)[1])

def _get_py3(html,one):
    if _get_sl(html) == 3:
        s = Py(hz = one,py1 = _get_py(html)[0],py1_herf = _get_fy(html)[0],py2 = _get_py(html)[1],py2_herf =_get_fy(html)[1],py3 = _get_py(html)[2],py3_herf = _get_fy(html)[2])

def _get_py4(html,one):
    if _get_sl(html) == 4:
        s = Py(hz = one,py1 = _get_py(html)[0],py1_herf = _get_fy(html)[0],py2 = _get_py(html)[1],py2_herf =_get_fy(html)[1],py3 = _get_py(html)[2],py3_herf = _get_fy(html)[2],py4 = _get_py(html)[3],py4_herf = _get_fy(html)[3])

def _get_py5(html,one):
    if _get_sl(html) == 5:
        s = Py(hz = one,py1 = _get_py(html)[0],py1_herf = _get_fy(html)[0],py2 = _get_py(html)[1],py2_herf =_get_fy(html)[1],py3 = _get_py(html)[2],py3_herf = _get_fy(html)[2],py4 = _get_py(html)[3],py4_herf = _get_fy(html)[3],py5 = _get_py(html)[4],py5_herf = _get_fy(html)[4])

def _get_py6(html,one):
    if _get_sl(html) == 6:
        s = Py(hz = one,py1 = _get_py(html)[0],py1_herf = _get_fy(html)[0],py2 = _get_py(html)[1],py2_herf =_get_fy(html)[1],py3 = _get_py(html)[2],py3_herf = _get_fy(html)[2],py4 = _get_py(html)[3],py4_herf = _get_fy(html)[3],py5 = _get_py(html)[4],py5_herf = _get_fy(html)[5],py6 = _get_py(html)[4],py6_herf = _get_fy(html)[5])

def _get_cz(ele,one):
    # 对搜索框里的内容清空，以便输入值
    ele.clear()
    # 字符串前面加u
    keyword = one + u'拼音'
    # 在百度搜索框输入值
    ele.send_keys(keyword)
    # 点击搜索

@db_session()
def task2():
    drive = _get_drive()
    f = codecs.open(r"e:\python\初始 - 副本.txt","r","utf-8-sig")
    # 打开百度网页
    drive.get('http://www.baidu.com')
    # 定位百度首页文本框
    ele = drive.find_element_by_id('kw')
    # 定位百度首页搜索框
    ele1 = drive.find_element_by_id('su')
    for line in f.readlines():
        for one in line.strip():
            _get_cz(ele,one)
            ele1.submit()
            time.sleep(3)
            html = drive.page_source
            _get_py1(html,one)
            _get_py2(html,one)
            _get_py3(html,one)
            _get_py4(html,one)
            _get_py5(html,one)
            _get_py6(html,one)
    f.close()
    drive.close()

# 对数据库进行处理
task1()
# 打开百度并在输入框中输入值点击搜索后将爬取到的对应的拼音和发音链接入库，以此往复
task2()
