# -*- coding: utf-8 -*-
"""
Created on Tue Jun 25 10:29:36 2024

@author: makej
"""
import json 
import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as st

"导入数据"
with open('brakes_fl.json','r',encoding='utf-8') as f:
    d=json.load(f)

cycle=[]
for i in d:
    for j in d[i]:
        for k in d[i][j]:
            for l in k:
                cycle.append(l[0])

"置信区间"
  
# create 90% and 95% confidence interval
CI_90=st.t.interval(0.90, df=len(cycle)-1,
              loc=np.mean(cycle),
              scale=st.sem(cycle))            
CI_95=st.t.interval(0.95, df=len(cycle)-1,
              loc=np.mean(cycle),
              scale=st.sem(cycle))    
print('置信区间为：0.9:{}，0.95：{}'.format(CI_90, CI_95))

"作图"
x=np.array(range(len(cycle)))
y=np.array(cycle)
plt.plot(x, y)

"90置信区间"
plt.plot([0,len(cycle)],[int(CI_90[0]),int(CI_90[0])],color='red',lw=2)
plt.plot([0,len(cycle)],[int(CI_90[1]),int(CI_90[1])],color='red',lw=2)

"95置信区间"
plt.plot([0,len(cycle)],[int(CI_95[0]),int(CI_95[0])],color='green',lw=2)
plt.plot([0,len(cycle)],[int(CI_95[1]),int(CI_95[1])],color='green',lw=2)

# "显示范围"
# plt.ylim((220,260))

plt.show()