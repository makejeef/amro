# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 10:05:26 2024

@author: makej
"""

import time,ddddocr,requests,json,csv,re,json
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
    elements_acesscode.send_keys('')

    elements_acesscode=driver.find_element(By.NAME,'userPassword')
    elements_acesscode.send_keys('')

    elements_acesscode=driver.find_element(By.NAME,'vCode')
    elements_acesscode.send_keys(res)

    elements_but=driver.find_element(By.ID,'btnSubmit').click()

    time.sleep(5)
    cookies = driver.get_cookies()
    return cookies
    driver.close()
"利用cookies获取工作包数据"

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
        data_list=data_str['data']
        return data_list
    else:
        print('no fl data')

    

if __name__ == '__main__':
    with open('wheels_time.json','r') as f:
        d=json.load(f)

    value_url='https://me.sichuanair.com/login.shtml'
    cookies=get_cookies(value_url)

    "几号轮子的磨损频率"
    "找出最大的时间间隔"
    times={'330':{},'350':{}}
    for ii in d:#每一个机型
        for i in d[ii]:#每一架飞机
            print(str(i)+'轮子更换频率')
            times[ii][i]=[[],[],[],[],[],[],[],[]]#某一架飞机对应的值是一个八个轮子的列表
            for j in range(8):
                print(str(j+1)+'号轮子')
                times[ii][i][j]=[]#某一个轮子的更换时间
                for k in range(len(d[ii][i][j])):#对应每一个轮子的更换更换日期
                    fl=get_fl(cookies, i, d[ii][i][j][k], d[ii][i][j][k+1])
                    times[ii][i][j].append(len(fl))
                    print(len(fl),d[ii][i][j][k][0:10],d[ii][i][j][k+1][0:10])
                    times[ii][i][j]
                    if k+2==len(d[ii][i][j]):
                        break

 
    
    
    
