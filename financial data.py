#!/usr/bin/env python
# coding: utf-8

# In[74]:


import pandas as pd
import numpy as np
import quandl
import matplotlib.pyplot as plt


# In[75]:


#Build a function to read dataset from Quandl and transform them into a standardized format,index:date,columns:Index Name,Index Columns
#The first parameter is the name of date from data sources.
#The second parameter is the name the user want to put under column 'Index Name'
#The third parameter is the column the user want to keep from the original dataset.Make sure the user take a look at data before doing the function and find out which index to keep as the Index Value.Keep contains two columns and the first is always 'Index Name'
def standardata(dataset,name,keep=['Index Name']):
    quandl.ApiConfig.api_key = "z2y5P4Yhy1YFZARoYStN"
    df1=quandl.get(dataset)
    df1.insert(loc=0,column='Index Name',value=name)
    for col in df1.columns:
        if col not in keep:
            df1.drop(columns=[col],inplace=True)
    df1.columns=['Index Name','Index Value']
    return df1


# In[128]:


nasdaq=standardata('NASDAQOMX/XQC',name='Nasdaq',keep=['Index Name','Index Value'])
nasdaq


# In[77]:


misery=standardata('USMISERY/INDEX',name='Misery',keep=['Index Name','Misery Index'])
misery


# In[78]:


#First comparision:
#Plot the two datasets from 2016-11-30 since we could only extract Nasdaq index from 2016-12-19.
#Hypothesis: We could briefly tell that nasdaq index and US misery index may have an inverse relationship by looking at data before and after April 2020
#Before April 2020,US misery index were decreasing while nasdaq index were increasing. However,on April 2020, US misery index had a sudden increase from 6 to 15(Maybe due to COVID-19)
#And nasdaq index had a tremendous decrease. We still need dataset comparasion to support our hypothesis. 
misery1=misery.loc['2016-11-30':]
fig,axes=plt.subplots(2,1,figsize=(15,15),sharex=True)
nasdaq.plot(ax=axes[0])
misery1.plot(ax=axes[1])


# In[79]:


#The first two functions are writen to be used in the third function, in order for split the datetime index to year and month
def splityear(date):
    return date.split('-')[0]
def splitmonth(date):
    return date.split('-')[1]

#To calculate the correlation index between Nasdaq index and Us misery index
def compcorr(dataset1,dataset2):
    #since misery are collected per month but nasdaq per day, so we have to calculate the average index per month on nasdaq to have a fair comparision with misery
    #reindex nasdaq and group the index values by year then month.
    ds=dataset1.reset_index()
    ds['Trade Date']=ds['Trade Date'].astype('string')
    ds['year']=ds['Trade Date'].apply(splityear)
    ds['month']=ds['Trade Date'].apply(splitmonth)
    #Calculate the average index per month and drop the values which are missing in misery
    ds=ds.groupby(['year','month'])['Index Value'].mean().reset_index().drop([30,31,42,43])
    
    #Left Join misery and nasdaq. Append the average values we calculated above to misery
    jointable=dataset1.merge(dataset2,how='right',left_index=True,right_index=True,suffixes=('_nasdaq','_misery'))
    jointable.drop(columns=['Index Name_nasdaq','Index Name_misery'],inplace=True)
    jointable=jointable[jointable.index>='2016-12-31'].drop(columns='Index Value_nasdaq')
    list=[]
    for i in ds['Index Value']:
        list.append(i)
    jointable['Index Value_nasdaq']=list
    
    return jointable.corr()


# In[80]:


#It turns out that our hypothesis might be wrong. They either have weak positive correlation or no relationship at all.
compcorr(nasdaq,misery)


# In[145]:


#Second comparision:
#Compare the daily return,eg: the daily return on 12/20/2016 is (value on 20th/value on 19th)-1=4953.80/4934.85-1=0.003840

def dailyreturn(dataset):
    ds2=dataset.reset_index().drop(0)
    list=[]
    for i in range(1,dataset.index.size):
        dreturn=dataset['Index Value'].iloc[i]/dataset['Index Value'].iloc[i-1]-1
        list.append(dreturn)
    ds2['daily return']=list
    return ds2
     
dr_nasq=dailyreturn(nasdaq)
dr_nasq


# In[146]:


dr_mi=dailyreturn(misery)
dr_mi


# In[149]:


#Averagely,Daily return of Us misery is higher than Nasdaq index
print(dr_nasq['daily return'].mean())
print(dr_mi['daily return'].mean())


# In[143]:


#Only draw the plot from Dec 2016. In general,daily return 
#We could tell that daily return of nasdaq is more stable than misery. March and April 2020 are most turbulent period for btoh indices.
#The conclusion may be biased because misery index was collected per month while Nasdaq index per day
dr_mi1=dr_mi[dr_mi['Date']>'2016-11-30']
plt.figure(figsize=(20,8),dpi=80)
plt.plot(dr_nasq['Trade Date'],dr_nasq['daily return'],label="nasdaq",color="red")
plt.plot(dr_mi1['Date'],dr_mi1['daily return'],label="misery",color="blue",linestyle="--")
plt.legend()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




