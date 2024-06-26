# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 08:41:43 2024

@author: makej
"""

import requests,time,json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By

"url列表"
url={'airnavx':'http://tp3.sichuanair.com:8000/airnavx/search/text',
         '320':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=300&msnBinding=%7B%22actype%22:%5B%22A318%22,%22A319%22,%22A320%22,%22A321%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=661498_SGML_C&searchFilter=&searchMode=document.toc',
         '330':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=21&msnBinding=%7B%22actype%22:%5B%22A330%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=654749_SGML_C&searchFilter=&searchMode=document.toc',
         '350':'http://tp3.sichuanair.com:8000/airnavx/api/filter/getFilter?filterType=tailNumber&maxResults=21&msnBinding=%7B%22actype%22:%5B%22A350%22%5D,%22customization%22:%5B%22CSC%22%5D%7D&revId=661146_S1KD_C&searchFilter=&searchMode=document.toc'
         }
"post_data列表"
"同一型号的飞机号列表"
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
                  'searchMode':'document.toc'}}
def get_cookies(url):
    driver=webdriver.Firefox()
    driver.implicitly_wait(5)
    driver.get(url)


    "输入账号密码进入airnav，获取cookies"
    elements_acesscode=driver.find_element(By.NAME,'access-code')
    elements_acesscode.send_keys('airbus123')

    driver.find_element(By.NAME,'submit').click()

    time.sleep(5)
    cookies = driver.get_cookies()
    return cookies
    driver.close() 
    
def get_fl(cookies):
    # session=requests.Session()
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
    return f
    




    
if __name__=='__main__':
    
    
    # fl_tn=input("飞机型号：")
    # fl_type=input("机号：")
    
    fl_cookies=get_cookies(url['airnavx'])

    fl_list=get_fl(fl_cookies)
    # print(fl_list)
    d={'320':fl_list[0],'330':fl_list[1],'350':fl_list[2]}
    # dataframe=pd.DataFrame.from_dict(d,orient='index')
    # dataframe.to_csv('fl.csv',index=False,sep=',')
    def save_dict(dictionary, file_path):
        with open(file_path, 'w') as file:
            json.dump(dictionary, file)
            
    save_dict(d,'fl.json')
    
    
    
    