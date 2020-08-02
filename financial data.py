#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import quandl
import matplotlib.pyplot as plt


# In[2]:


#Build a function to read dataset from Quandl and transform them into a standardized format,index:date,columns:Index Name,Index Columns
#The first parameter is the name of date from data sources.
#The second parameter is the name the user want to put under column 'Index Name'
#The third and fourth parameter are start date and end date that the user want to extract data
#The third parameter is the column the user want to keep from the original dataset.Make sure the user take a look at data before doing the function and find out which index to keep as the Index Value.Keep contains two columns and the first is always 'Index Name'
def standardata(dataset,name,s_date, e_date,keep=['Index Name']):
    quandl.ApiConfig.api_key = "z2y5P4Yhy1YFZARoYStN"
    df1=quandl.get(dataset,start_date=s_date,end_date=e_date)
    df1.insert(loc=0,column='Index Name',value=name)
    for col in df1.columns:
        if col not in keep:
            df1.drop(columns=[col],inplace=True)
    df1.columns=['Index Name','Index Value']
    return df1


# In[3]:


nasdaq=standardata('NASDAQOMX/XQC',name='Nasdaq',s_date='2003-01-20',e_date='2020-07-30',keep=['Index Name','Index Value'])
nasdaq


# In[4]:


#Since we could only extract Nasdaq Index from 2016-12-19 till now, we will extract US misery index from Dec 2016 in order to compare them
misery=standardata('USMISERY/INDEX',name='Misery',s_date='2016-12-01',e_date='2020-07-30',keep=['Index Name','Misery Index'])
misery


# In[5]:


#First comparision:
#Hypothesis: We could briefly tell that nasdaq index and US misery index may have an inverse relationship by looking at data before and after April 2020
#Before April 2020,US misery index were decreasing while nasdaq index were increasing. However,on April 2020, US misery index had a sudden increase from 6 to 15(Maybe due to COVID-19)
#And nasdaq index had a tremendous decrease. We still need dataset comparasion to support our hypothesis. 
fig,axes=plt.subplots(2,1,figsize=(15,15),sharex=True)
nasdaq.plot(ax=axes[0])
misery.plot(ax=axes[1])


# In[6]:


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
    ds['Trade Date']=ds['Trade Date'].astype('str')
    ds['year']=ds['Trade Date'].apply(splityear)
    ds['month']=ds['Trade Date'].apply(splitmonth)
    #Calculate the average index per month and drop the values which are missing in misery
    ds=ds.groupby(['year','month'])['Index Value'].mean().reset_index().drop([30,31,42,43])
    
    #Left Join misery and nasdaq. Append the average values we calculated above to misery
    jointable=dataset1.merge(dataset2,how='right',left_index=True,right_index=True,suffixes=('_nasdaq','_misery'))
    jointable.drop(columns=['Index Name_nasdaq','Index Name_misery'],inplace=True)
    jointable=jointable.drop(columns='Index Value_nasdaq')
    list=[]
    for i in ds['Index Value']:
        list.append(i)
    jointable['Index Value_nasdaq']=list
    
    return jointable.corr()


# In[7]:


#It turns out that our hypothesis might be wrong. They either have weak positive correlation or no relationship at all.
compcorr(nasdaq,misery)


# In[8]:


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

#Split nasdaq "Trade Date" into year and month. Groupby year then month and get the first and last element in each month

nasdaq=nasdaq.reset_index()

nasdaq['year']=nasdaq['Trade Date'].astype('str').apply(splityear)
nasdaq['month']=nasdaq['Trade Date'].astype('str').apply(splitmonth)
dr_nasq=nasdaq.groupby(['year','month']).agg(['first','last']).reset_index()
dr_nasq


# In[9]:


#Calculate the monthly return use the method above, then drop the first level in multindex dataframe
for i in dr_nasq:
    dr_nasq['monthly return']=dr_nasq['Index Value']['first']/dr_nasq['Index Value']['last']-1
mr_nasq=dr_nasq.copy(deep=True)
mr_nasq.columns=dr_nasq.columns.droplevel(1)

#Get the year-month element then assign it to a new column in order to draw plot later
lst=[]
for i in mr_nasq.index:
    lst.append(mr_nasq.iloc[i]['year']+'-'+mr_nasq.iloc[i]['month'])

#Remove redundant columns and change 'date' column to datetime
mr_nasq['date']=lst
mr_nasq.drop(columns=['Index Name','year','month'],inplace=True)
mr_nasq['date']=pd.to_datetime(mr_nasq['date']).apply(lambda x:x.strftime('%Y-%m'))

mr_nasq


# In[10]:


mr_mi=dailyreturn(misery).rename(columns={'daily return':'monthly return'})
mr_mi['Date']=mr_mi['Date'].apply(lambda x:x.strftime('%Y-%m'))
mr_mi


# In[11]:


#Averagely,monthly return of Us misery is higher than Nasdaq index
print(mr_nasq['monthly return'].mean())
print(mr_mi['monthly return'].mean())


# In[12]:


#We could tell that monthly return of nasdaq is more stable than misery. March and April 2020 are most turbulent period for btoh indices.

plt.figure(figsize=(30,8),dpi=80)
plt.plot(mr_nasq['date'],mr_nasq['monthly return'],label="nasdaq",color="red")
plt.plot(mr_mi['Date'],mr_mi['monthly return'],label="misery",color="blue",linestyle="--")
plt.legend()


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




