# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 09:37:04 2024

@author: makej
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

import time,ddddocr,requests,json,re,json

#获取网站cookies
def get_cookies(url):
    "获取网页信息"
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    
    driver.get(url)

    #等待五秒
    #wait = WebDriverWait(driver, 5)
    time.sleep(3)
    "获取验证码"
    #elements_acesscode=driver.find_element(By.ID,'')
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
    driver.close()
    return cookies

#工作包换轮时间
def get_wheels_time(*kw):
    "requests使用selenium获取的cookies，来模拟登录获取相关数据"
    session=requests.Session()
    cookies={cookie['name']: cookie['value'] for cookie in kw[0]}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
    url_workorder='https://me.sichuanair.com/api/v1/plugins/LM_WORKORDER_LIST'
    if len(kw)==4:
        postdata_330={"planstd":"{}".format(kw[1]),
                    "planend":"{}".format(kw[2]),
                    "keyWord":"前轮",
                    "keyWordStr":"前轮",
                    "actypeStr": "()",
                    "acno": "{}".format(kw[3]),
                    "page":"1",
                    "rows":"9999"}
    else:
        postdata_330={"planstd":"{}".format(kw[1]),
                    "planend":"{}".format(kw[2]),
                    "keyWord":"前轮",
                    "keyWordStr":"前轮",
                    "actypeStr": "()",
                    "page":"1",
                    "rows":"9999"}
        
    
    l=session.post(url_workorder,headers=headers,data=postdata_330,cookies=cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        data_list=data_str['data']
        def whrp1(d):
            if 'FK_INFO' in d:
                if re.search('更换',d['FK_INFO']):
                    return d
        def whrp2(d):
            if 'ATA' in d:
                if d['ATA'][0:5]=='32-41':
                    return d
        
            
        whrp=list(filter(whrp1,data_list))#筛选更换工作包
        whrp_data=list(filter(whrp2,whrp))#筛选章节号‘32-41’工作包

        
    else:
        print('no data')
        
    with open('fl.json','r') as f:
         fl=json.load(f)

    d={'330':{},'350':{}}
    for i in fl['330']:#i飞机号
        d['330'][i]=[[],[]] #两个个轮子的更换时间的列表
        for j in whrp_data:
            if j['TASKSTS']=='FC':
                if j['ACNO']==i:
                    cnNumber=['左','右']
                    for k in range(2):#左右前轮
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])

       
    for i in fl['350']:#区分飞机号
        d['350'][i]=[[],[]] #八个轮子的更换时间的列表
        for j in whrp_data:
            if j['ACNO']==i:
                if j['TASKSTS']=='FC':
                    if j['ACNO']==i:
                        cnNumber=['左','右']
                        for k in range(2):
                            pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                            if re.search(pattern,j['FK_INFO']):
                                # print('更换{}号主轮'.format(cnNumber[k]))
                                d['350'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
                    

    return d

#每两次换轮之间的循环次数
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
    url='https://me.sichuanair.com/login.shtml'
    cookies=get_cookies(url)
    
    start_date=input('start_date:')
    end_date=input('end_date:')
    kw=[cookies,start_date,end_date]
    d=get_wheels_time(*kw)
    
    times={'330':{},'350':{}}

    for ii in d:#ii:机型
        for i in d[ii]:#i：飞机号
            # print(str(i)+'前轮更换频率')
            times[ii][i]=[[],[]]#某一架飞机对应的值是一个两个个轮子的列表
            for j in range(2):#j:轮子号
                # print(str(j+1)+'号轮')
                times[ii][i][j]=[]#某一个轮子的更换时间
                if len(d[ii][i][j])>1:
                    for k in range(len(d[ii][i][j])):#对应每一个轮子的更换更换日期
                        fl=get_fl(cookies, i, d[ii][i][j][k][0:10], d[ii][i][j][k+1][0:10])
                        times[ii][i][j].append([len(fl),d[ii][i][j][k], d[ii][i][j][k+1]])
                        # if len(fl)<150 or len(fl)>300:
                        #     print(len(fl),d[ii][i][j][k],d[ii][i][j][k+1])
                        # else:
                        #     print(len(fl))
                        # times[ii][i][j]
                        if k+2==len(d[ii][i][j]):
                            break
                
    
    # def save_dict(dictionary, file_path):
    #     with open(file_path, 'w') as file:
    #         json.dump(dictionary, file)
            
    # save_dict(times,'nose_wheels_fl.json')
    
    cycle={'330':[],'350':[]}
    for i in times:
        for j in times[i]:#某一个机型的循环
            for k in times[i][j]:#某一个机号的循环
                for l in k:
                    cycle[i].append(l[0])
    
    plot_img(cycle['330'])
    plot_img(cycle['350'])