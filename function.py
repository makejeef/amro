# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 10:05:26 2024

@author: makej
"""

import time,ddddocr,requests,json,csv,re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

"获取cookies"
def get_cookies(url):
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(url)

    time.sleep(3)
    "获取验证码"
    elements_acesscode=driver.find_element(By.ID,'img_vcode').screenshot("a.jpg")

    ocr = ddddocr.DdddOcr()              # 实例化
    with open('a.jpg', 'rb') as f:     # 打开图片
        img_bytes = f.read()             # 读取图片
    res = ocr.classification(img_bytes)  # 识别
    #print(res)


    "输入账号密码进入amro，获取cookies"
    elements_acesscode=driver.find_element(By.NAME,'username')
    elements_acesscode.send_keys('018608')

    elements_acesscode=driver.find_element(By.NAME,'userPassword')
    elements_acesscode.send_keys('7400233@scal')

    elements_acesscode=driver.find_element(By.NAME,'vCode')
    elements_acesscode.send_keys(res)

    elements_but=driver.find_element(By.ID,'btnSubmit').click()

    time.sleep(5)
    cookies = driver.get_cookies()
    return cookies
    driver.close()
"利用cookies获取工作包数据"
# def get_wo(cookies,fln):
#     session=requests.Session()
#     cookies={cookie['name']: cookie['value'] for cookie in cookies}
#     headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
#     url_workorder='https://me.sichuanair.com/api/v1/plugins/LM_WORKORDER_LIST'
#     post_data={"planstd":"2023-01-04 08:00:00",
#                 "planend":" 2024-04-05 08:00:00",
#                 "ifClose":"",
#                 "order":"asc",
#                 "keyWord":"主轮",
#                 "keyWordStr":"主轮",
#                 "acno":"{}".format(fln),
#                 "page":"1",
#                 "rows":"999"}
#     l=session.post(url_workorder,headers=headers,data=post_data,cookies=cookies)
#     if l.status_code==200:
#         json_data=l.content.decode('utf-8')
#         data_str=json.loads(json_data)
#         wodata_list=data_str['data']
#         whrp_data=[i for i in wodata_list if re.search('更换',i['MDTITLE_C'])]#列表解析方法
#         # rp_date=[l['ACTUEND'].split(' ')[0] for l in whrp_data ]
#         "循环出八个主轮更换日期数据"
#         #print(whrp_data)
#         wh_date=[]
#         for i in range(8):
#             wh_date.append([j['ACTUEND'].split(' ')[0] for j in whrp_data if re.search('{}'.format(i+1),j['MDTITLE_C'])])
#         return wh_date
#     else:
#         print('no wo data')
# "航班数据,返回的是时间内航段的列表"
def get_fl(cookies,fln,start_date,end_date):
    session=requests.Session()
    cookies={cookie['name']: cookie['value'] for cookie in cookies}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
    url_workorder='https://me.sichuanair.com/api/v1/plugins/LM_FLIGHT_SEARCH_LIST'
    post_data={"flightDate":"{}".format(start_date),
                "flightDate1":"{}".format(end_date),
                "actype1":"()",
                "acno":"{}".format(fln),
                "page":"1",
                "rows":"999"}
    l=session.post(url_workorder,headers=headers,data=post_data,cookies=cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        # pages=data_str['page']
        data_list=data_str['data']
        return data_list
    else:
        print('no fl data')

    

if __name__ == '__main__':
    data=pd.read_csv('350.csv')
    
    value_fln=input('请输入飞机号：')
    wheel_num=input('请输入几号轮子:')
    value_url='https://me.sichuanair.com/login.shtml'
    value_cookies=get_cookies(value_url)
    "获取换轮时间"
    wheels_date=get_wo(value_cookies, value_fln)
   
    "几号轮子的磨损频率"
    dw=wheels_date[int(wheel_num)]#更换某一处轮子日期数量
    wheel_freq=[]#两次之间的起降次数
    #fl_num=[]
    for i in range(len(dw)-1):
        fl_num=get_fl(value_cookies,value_fln,dw[i],dw[i+1])
        wheel_freq.append(len(fl_num))
        if i==range(len(dw)-1):
            break
    print(wheel_freq)
    
    
    
    
    