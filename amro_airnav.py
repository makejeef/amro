# -*- coding: utf-8 -*-
"""
Created on Tue May 14 09:26:45 2024

@author: makej
"""
import requests,time,json,ddddocr,re

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

"url池子"
url={'airnavx':'http://tp3.sichuanair.com:8000/airnavx/search/text',
     'amro':'https://me.sichuanair.com/login.shtml',
     'wo':'https://me.sichuanair.com/api/v1/plugins/LM_WORKORDER_LIST',
     'fl':'https://me.sichuanair.com/api/v1/plugins/LM_FLIGHT_SEARCH_LIST',
     '320':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=300&msnBinding=%7B%22actype%22:%5B%22A318%22,%22A319%22,%22A320%22,%22A321%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=661498_SGML_C&searchFilter=&searchMode=document.toc',
     '330':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=21&msnBinding=%7B%22actype%22:%5B%22A330%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=654749_SGML_C&searchFilter=&searchMode=document.toc',
     '350':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=21&msnBinding=%7B%22actype%22:%5B%22A350%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=661146_S1KD_C&searchFilter=&searchMode=document.toc'
             }
'post池子'
post_data={'320':{'filterType': 'tailNumber',
                  'maxResults': '300',
                  'msnBinding': {"actype":["A318","A319","A320","A321"],"customization":["CSC"]},
                  'revId': '661498_SGML_C',
                  'searchMode': 'document.toc'},
           '330':{'filterType': 'tailNumber',
                  'maxResults': '21',
                  'msnBinding': {"actype":["A330"],"customization":["CSC"]},
                  'revId': '654749_SGML_C',
                  'searchMode':'document.toc'},
           '350':{'filterType': 'tailNumber',
                  'maxResults': '21',
                  'msnBinding': {"actype":["A350"],"customization":["CSC"]},
                  'revId': '661146_S1KD_C',
                  'searchMode':'document.toc'},
         
           }

"获取所有飞机号"
def get_flight():
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(url['airnavx'])


    "输入账号密码进入airnav，获取cookies"
    elements_acesscode=driver.find_element(By.NAME,'access-code')
    elements_acesscode.send_keys('airbus123')

    driver.find_element(By.NAME,'submit').click()

    time.sleep(5)
    cookies = driver.get_cookies()
    # return cookies
    driver.close()
    
    air_cookies={cookie['name']: cookie['value'] for cookie in cookies}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}

    "需要看清楚是get还是post方法"
    f=[]
    f_type=['320','330','350']
    for t in f_type:
        # l=session.post(url['330'],data=post_data['330'],headers=headers,cookies=air_cookies)
        l=requests.get(url[t],data=post_data[t],headers=headers,cookies=air_cookies)
        if l.status_code==200:
            json_data=l.content.decode('utf-8')
            data_str=json.loads(json_data)
            fln_list=data_str['results']
            # print(fln_list)
            fl=[i['aircraftDetail'][0][0:6] for i in fln_list]
            f.append(fl)
            # return fl
        
        else:
            print('no data')
            
    f_dict=dict(zip(f_type,f))
    
    return f_dict

"amro每一架飞机轮子的频率"
def get_cookies():
    "模拟登录得到amro的cookies"
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(url['amro'])

    time.sleep(3)
    "获取验证码"
    elements_acesscode=driver.find_element(By.ID,'img_vcode').screenshot("a.jpg")

    ocr = ddddocr.DdddOcr()              # 实例化
    with open('a.jpg', 'rb') as f:     # 打开图片
        img_bytes = f.read()             # 读取图片
    res = ocr.classification(img_bytes)  # 识别


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
    driver.close()
    return cookies
    
def get_wo(tn,start,end,cookies):#工作包内容
    # cookies=get_cookies()
    "使用cookies 获取工作包内容"
    postdata_wo={"planstd":"{} 08:00:00".format(start),
                "planend":" {} 08:00:00".format(end),
                "keyWord":"主轮",
                "keyWordStr":"主轮",
                "actypeStr": "({})".format(tn),
                "actype": "{}".format(tn),
                "page":"1",
                "rows":"999"}
    
    session=requests.Session()
    cookies={cookie['name']: cookie['value'] for cookie in cookies}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
    l=session.post(url['wo'],headers=headers,data=postdata_wo,cookies=cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        wodata_list=data_str['data']
        whrp_data=[i for i in wodata_list if re.search('更换',i['MDTITLE_C'])]#列表解析方法
 
    return whrp_data

def get_flsearch(tn,t1,t2):#时间间隔内的起降次数
    cookies=get_cookies()

    "根据更换的时间，得到两次之间的起降次数"
    session=requests.Session()
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
    postdata_fl={"flightDate":"{}".format(t1),
                "flightDate1":"{}".format(t2),
                "actype1":"()",
                "acno":"{}".format(tn),
                "page":"1",
                "rows":"999"}
    l=session.post(url['fl'],headers=headers,data=postdata_fl,cookies=cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        # pages=data_str['page']
        data_list=data_str['data']
        return data_list
    else:
        print('no fl data')

if __name__=='__main__':
    "得到所有飞机的字典列表"
    fl=get_flight()
    
    # dataframe=pd.DataFrame.from_dict(d,orient='index')
    # dataframe.to_csv('fl.csv',index=False,sep=',')
    
    "根据飞机类型得到所有的飞机的更换轮子的工作包"
    start='2023-01-01'
    end='2024-01-01'
    wo={}
    d={}#定义一个飞机号和换轮时间的映射

    "循环出三类飞机的换轮日期"
    cookies=get_cookies()
    for i in fl.keys():
        wo[i]=(get_wo(i, start, end,cookies))#wo[i]每一类飞机的换轮工作包
        for j in fl[i]:#fl[i]是某一类飞机号列表
            d[j]=[]#每个飞机号对应的值为一个列表
            for k in wo[i]:#工作包附在飞机号的后面
                if k['ACNO']==j:
                    d[j].append(k['EN_DT'][0:10])
                    
            
            
                    
    
    