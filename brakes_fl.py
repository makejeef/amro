# -*- coding: utf-8 -*-
"""
Created on Mon Jul 29 12:00:48 2024

@author: makej
"""


import time,ddddocr,requests,json,csv,re,json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

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
    username=input("username:")
    elements_acesscode.send_keys(username)

    elements_acesscode=driver.find_element(By.NAME,'userPassword')
    password=input("password:")
    elements_acesscode.send_keys(password)

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
                "rows":"9999"}
    l=session.post(url_workorder,headers=headers,data=post_data,cookies=cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        data_list=data_str['data']
        return data_list
    else:
        print('no fl data')

def plot_img(data):
    "置信区间"
      
    # create 90% and 95% confidence interval
    CI_90=st.t.interval(0.90, df=len(data)-1,
                  loc=np.mean(data),
                  scale=st.sem(data))            
    CI_95=st.t.interval(0.95, df=len(data)-1,
                  loc=np.mean(data),
                  scale=st.sem(data))    
    print('置信区间为：0.9:{}，0.95：{}'.format(CI_90, CI_95))

    "作图"
    x=np.array(range(len(data)))
    y=np.array(data)
    plt.plot(x, y)

    "90置信区间"
    plt.plot([0,len(data)],[int(CI_90[0]),int(CI_90[0])],color='red',lw=2)
    plt.plot([0,len(data)],[int(CI_90[1]),int(CI_90[1])],color='red',lw=2)

    "95置信区间"
    plt.plot([0,len(data)],[int(CI_95[0]),int(CI_95[0])],color='green',lw=2)
    plt.plot([0,len(data)],[int(CI_95[1]),int(CI_95[1])],color='green',lw=2)

    # "显示范围"
    # plt.ylim((220,260))

    plt.show()

if __name__ == '__main__':
    with open('brakes_time.json','r',encoding=('utf-8')) as f:
        d=json.load(f)

    value_url='https://me.sichuanair.com/login.shtml'
    cookies=get_cookies(value_url)

    "几号刹车的磨损频率"
    "找出最大的时间间隔"
    times={'330':{},'350':{}}

    for ii in d:#ii:机型
        for i in d[ii]:#i：飞机号
            # print(str(i)+'刹车更换频率')
            times[ii][i]=[[],[],[],[],[],[],[],[]]#某一架飞机对应的值是一个八个刹车的列表
            for j in range(8):#j:刹车号
                # print(str(j+1)+'号刹车')
                times[ii][i][j]=[]#某一个刹车的更换时间
                for k in range(len(d[ii][i][j])):#对应每一个轮子的更换更换日期
                    if len(d[ii][i][j])>1:
                        fl=get_fl(cookies, i, d[ii][i][j][k][0:10], d[ii][i][j][k+1][0:10])
                        times[ii][i][j].append([len(fl),d[ii][i][j][k], d[ii][i][j][k+1]])
                        # print(len(fl),d[ii][i][j][k],d[ii][i][j][k+1])
                        # times[ii][i][j]
                        if k+2==len(d[ii][i][j]):
                            break
                    
    cycle={'330':[],'350':[]}
    for i in times:
        for j in times[i]:#某一个机型的循环
            for k in times[i][j]:#某一个机号的循环
                for l in k:
                    cycle[i].append(l[0])
    
    plot_img(cycle['330'])
    plot_img(cycle['350'])
# def save_dict(dictionary, file_path):
#     with open(file_path, 'w',encoding='utf-8') as file:
#         json.dump(dictionary, file,ensure_ascii=False)
        
# save_dict(times,'brakes_fl.json')