# -*- coding: utf-8 -*-
"""
Created on Fri Aug  2 09:09:21 2024

@author: makej
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

import time,ddddocr,requests,json,re

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
    
def get_wo(tn,start,end,cookies):#工作包内容
    # cookies=get_cookies()
    "使用cookies 获取工作包内容"
    postdata_wo={"planstd":"{} 08:00:00".format(start),
                "planend":"{} 08:00:00".format(end),
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

"得到最新换轮日期"

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

def save_dict(dictionary, file_path):
    with open(file_path, 'w',encoding='utf-8') as file:
        json.dump(dictionary, file,ensure_ascii=False)        
    

if __name__=='__main__':

    with open('fl.json','r') as f:
         fl=json.load(f)
         
    t=time.localtime()
    
    start='2024-01-01'
    end=str(t.tm_year)
    if t.tm_mon<10:
        end=end+'-0'+str(t.tm_mon)
    else:
        end=end+'-'+str(t.tm_mon)
    if t.tm_mday<10:
        end=end+'-0'+str(t.tm_mday)
    else:
        end=end+'-'+str(t.tm_mday)    
        
    
    wo={}
    d={}#定义一个飞机号和换轮时间的映射

    "循环出三类飞机的换轮日期"
    cookies=get_cookies(url['amro'])
    
    d={'330':{},'350':{}}
    whrp_data=get_wo('A330', start, end, cookies)
    for i in fl['330']:#i飞机号
        d['330'][i]=[[],[],[],[],[],[],[],[]] #八个轮子的更换时间的列表
        
        for j in whrp_data:
            if j['TASKSTS']=='FC':
                if j['ACNO']==i:
                    cnNumber=['一','二','三','四','五','六','七','八']
                    for k in range(8):#k号主轮
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])

    whrp_data=get_wo('A350', start, end, cookies)   
    for i in fl['350']:#区分飞机号
        d['350'][i]=[[],[],[],[],[],[],[],[]] #八个轮子的更换时间的列表
        for j in whrp_data:
            if j['ACNO']==i:
                if j['TASKSTS']=='FC':
                    if j['ACNO']==i:
                        cnNumber=['一','二','三','四','五','六','七','八']
                        for k in range(8):
                            pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                            if re.search(pattern,j['FK_INFO']):
                                # print('更换{}号主轮'.format(cnNumber[k]))
                                d['350'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
    "得到最新换轮时间"
    date={'330':{},'350':{}}
    for i in d:
        for j in d[i]:
            date[i][j]=[[],[],[],[],[],[],[],[]]
            for k in range(8):
                if d[i][j][k]!=[]:
                    date[i][j][k]=d[i][j][k][-1][0:10]
    
    "得到已经使用循环"
    wheel_fl={'330':{},'350':{}}
    
    for i in fl['330']:
        wheel_fl['330'][i]=[[],[],[],[],[],[],[],[]]
        for j in range(8):
            wheel_fl['330'][i][j]=len(get_fl(cookies, i, date['330'][i][j], end))
 
    for i in fl['350']:
        wheel_fl['350'][i]=[[],[],[],[],[],[],[],[]]
        for j in range(8):
            wheel_fl['350'][i][j]=len(get_fl(cookies, i, date['350'][i][j], end))

            
    save_dict(wheel_fl,'wheels_fl.json')

        
            