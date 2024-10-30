# -*- coding: utf-8 -*-
"""
Created on Mon Oct 14 10:23:15 2024

@author: makej
"""
from selenium import webdriver
from selenium.webdriver.common.by import By

import time,ddddocr,requests,json,re,json

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

#工作包前换轮时间
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
        d['330'][i]=[[],[]] #两个轮子的更换时间的列表
        for j in whrp_data:
            if j['TASKSTS']=='FC':
                if j['ACNO']==i:
                    cnNumber=['左','右']
                    for k in range(2):#左右前轮
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            print('更换{}号前轮'.format(cnNumber[k]))
                            d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])

       
    for i in fl['350']:#区分飞机号
        d['350'][i]=[[],[]] #两个轮子的更换时间的列表
        for j in whrp_data:
            if j['ACNO']==i:
                if j['TASKSTS']=='FC':
                    if j['ACNO']==i:
                        cnNumber=['左','右']
                        for k in range(2):
                            pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                            if re.search(pattern,j['FK_INFO']):
                                print('更换{}号前轮'.format(cnNumber[k]))
                                d['350'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
                    

    return d

#工作包换主轮时间

def get_mainwheels_time(*kw):
    "requests使用selenium获取的cookies，来模拟登录获取相关数据"
    session=requests.Session()
    cookies={cookie['name']: cookie['value'] for cookie in kw[0]}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
    url_workorder='https://me.sichuanair.com/api/v1/plugins/LM_WORKORDER_LIST'
    if len(kw)==4:
        postdata_330={"planstd":"{}".format(kw[1]),
                    "planend":"{}".format(kw[2]),
                    "keyWord":"主轮",
                    "keyWordStr":"主轮",
                    "actypeStr": "()",
                    "acno": "{}".format(kw[3]),
                    "page":"1",
                    "rows":"9999"}
    else:
        postdata_330={"planstd":"{}".format(kw[1]),
                    "planend":"{}".format(kw[2]),
                    "keyWord":"主轮",
                    "keyWordStr":"主轮",
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
        d['330'][i]=[[],[],[],[],[],[],[],[]] #轮子的更换时间的列表
        for j in whrp_data:
            if j['TASKSTS']=='FC':
                if j['ACNO']==i:
                    cnNumber=['一','二','三','四','五','六','七','八']
                    for k in range(8):#左右前轮
                        pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                        if re.search(pattern,j['FK_INFO']):
                            print('更换{}号主轮'.format(cnNumber[k]))
                            d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])

       
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
                                print('更换{}号主轮'.format(cnNumber[k]))
                                d['350'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
                    

    return d

def get_brakestime(*kw):
    session=requests.Session()
    cookies={cookie['name']: cookie['value'] for cookie in kw[0]}
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',}
    url_workorder='https://me.sichuanair.com/api/v1/plugins/LM_WORKORDER_LIST'
    postdata_330={"planstd":"2019-01-04 08:00:00",
                "planend":" 2024-07-29 08:00:00",
                # "ifClose":"",
                # "order":"asc",
                "keyWord":"刹车",
                "keyWordStr":"刹车",
                "actypeStr": "(A330|350)",
                "actype": "A330,A350",
                "page":"1",
                "rows":"9999"}
    l=session.post(url_workorder,headers=headers,data=postdata_330,cookies=cookies)
    if l.status_code==200:
        json_data=l.content.decode('utf-8')
        data_str=json.loads(json_data)
        data_list=data_str['data']
        whrp_data=[i for i in data_list if re.search('更换',i['MDTITLE_C'])]

    else:
        print('no data')

    "飞机号导入"
    with open('fl.json','r') as f:
         fl=json.load(f)

    d={'330':{},'350':{}}
    for i in fl['330']:#i飞机号
        d['330'][i]=[[],[],[],[],[],[],[],[]] #八个刹车的更换时间的列表
        for j in whrp_data:
            if j['TASKSTS']=='FC':
                if 'ACNO' in j:
                    if j['ACNO']==i:
                        cnNumber=['一','二','三','四','五','六','七','八']
                        for k in range(8):#k号刹车
                            pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                            if re.search(pattern,j['FK_INFO']):
                                print('更换{}号刹车'.format(cnNumber[k]))
                                d['330'][i][k].append(j['ACTUEND'][0:10]+j['FK_INFO'])
                    

       
    for i in fl['350']:#区分飞机号
        d['350'][i]=[[],[],[],[],[],[],[],[]] #八个刹车的更换时间的列表
        for j in whrp_data:
            if j['TASKSTS']=='FC':
                if 'ACNO' in j:
                    if j['ACNO']==i:
                        cnNumber=['一','二','三','四','五','六','七','八']
                        for k in range(8):
                            pattern='更换.*?({}|{})'.format(k+1,cnNumber[k])
                            if re.search(pattern,j['FK_INFO']):
                                print('更换{}号刹车'.format(cnNumber[k]))
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
        
        
if __name__ == '__main__':
    
    value_url='https://me.sichuanair.com/login.shtml'
    cookies=get_cookies(value_url)
    
    start_date=input('start_date:')
    end_date=input('end_date:')
    kw=[cookies,start_date,end_date]
    
    "得到更换时间"
    nose=get_wheels_time(*kw)
    main=get_mainwheels_time(*kw)
    brake=get_brakestime(*kw)
    
    "得到更换的起飞循环次数"
    nose_time={'330':{},'350':{}}

    for ii in nose:#ii:机型
        for i in nose[ii]:#i：飞机号
            # print(str(i)+'前轮更换频率')
            nose_time[ii][i]=[[],[]]#某一架飞机对应的值是一个两个个轮子的列表
            for j in range(2):#j:轮子号
                # print(str(j+1)+'号轮')
                nose_time[ii][i][j]=[]#某一个轮子的更换时间
                if len(nose[ii][i][j])>1:
                    for k in range(len(nose[ii][i][j])):#对应每一个轮子的更换更换日期
                        fl=get_fl(cookies, i, nose[ii][i][j][k][0:10], nose[ii][i][j][k+1][0:10])
                        nose_time[ii][i][j].append([len(fl),nose[ii][i][j][k], nose[ii][i][j][k+1]])
    
    main_time={'330':{},'350':{}}

    for ii in main:#ii:机型
        for i in main[ii]:#i：飞机号
            # print(str(i)+'前轮更换频率')
            main_time[ii][i]=[[],[]]#某一架飞机对应的值是一个两个个轮子的列表
            for j in range(8):#j:轮子号
                # print(str(j+1)+'号轮')
                main_time[ii][i][j]=[]#某一个轮子的更换时间
                if len(main[ii][i][j])>1:
                    for k in range(len(main[ii][i][j])):#对应每一个轮子的更换更换日期
                        fl=get_fl(cookies, i, main[ii][i][j][k][0:10], main[ii][i][j][k+1][0:10])
                        main_time[ii][i][j].append([len(fl),main[ii][i][j][k], main[ii][i][j][k+1]])
    
                        
    brake_time={'330':{},'350':{}}            
    
    for ii in brake:#ii:机型
        for i in brake[ii]:#i：飞机号
            # print(str(i)+'前轮更换频率')
            brake_time[ii][i]=[[],[]]#某一架飞机对应的值是一个两个个轮子的列表
            for j in range(8):#j:轮子号
                # print(str(j+1)+'号轮')
                brake_time[ii][i][j]=[]#某一个轮子的更换时间
                if len(brake[ii][i][j])>1:
                    for k in range(len(brake[ii][i][j])):#对应每一个轮子的更换更换日期
                        fl=get_fl(cookies, i, brake[ii][i][j][k][0:10], brake[ii][i][j][k+1][0:10])
                        brake_time[ii][i][j].append([len(fl),brake[ii][i][j][k], brake[ii][i][j][k+1]])
    