#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from bs4 import BeautifulSoup as bs
import time
import re
from urllib.request import urlopen
import pandas as pd, numpy as np
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import os
import bcpandas
from bcpandas import SqlCreds, to_sql

from datetime import date
from datetime import datetime


# ### mainclass

# In[2]:


class Scrape :
    
    def __init__(self,objectnumber) :
        self.objectnumber = objectnumber
                    
    def GetLink(self,kode_kota,page) :
        #retrieve tokopedia merchant link
        self.op = webdriver.ChromeOptions()
        self.driver = webdriver.Chrome('Your webdriver location')
        self.op.add_argument('headless')
        self.kode_kota = kode_kota
        self.page = page
        self.df=pd.DataFrame()
        self.driver.get('https://www.tokopedia.com/search?st=shop&fcity='+self.kode_kota+'&page='+str(self.page+1))
        time.sleep(5)
        try:
            self.source = self.driver.page_source
            self.data=bs(self.source, 'html.parser')
            self.body = self.data.find('body')
            self.script = self.body.find('div', attrs={'class':'css-rjanld'})
            for i in self.body.findAll('div', attrs = {'class':'css-r9pe88'}): 
                self.url=i.a['href'] 
                self.df = self.df.append({'url':self.url}, ignore_index=True)
        except :
            print("Link Failed to take")
    
    def GetTokofile(self) :
        #Retrieve merchant info
        self.Data=pd.DataFrame(index=range(0,len(self.df)),columns={"toko":[],"awal_buka":[],"alamat":[],"nomorhp":[],"daerah":[],"kd_daerah":[],"kd_page":[],"kurir":[],"transaksi":[],"rating":[],"desc":[],"url":[],"tgl_Scrapping":[]})
        self.listtoko=self.df['url'].tolist()
        for i in range(len(self.listtoko)) :
            try :
                #self.driver.find_element_by_css_selector("body > div:nth-child(40) > div.css-135pzkf-unf-coachmark.ety06v11 > section > div > div > div.unf-coachmark__action-wrapper.css-1xhj18k.ety06v13 > div").click()
                time.sleep(1)
                self.driver.get(self.listtoko[i])
                time.sleep(2)
                self.driver.find_element_by_css_selector("#zeus-root > div > div.css-zvvilv > div.css-1gwt8mt > div > div > div.css-3jbqnj.e1ufc1ph0 > div > div > div.css-1p0pkw3.e1ufc1ph0 > div.css-ais6tt > button.css-62yvak-unf-btn.e1ggruw00").click()
                time.sleep(1)
                self.soup=bs(self.driver.page_source)
                time.sleep(1)
                if self.soup.find("h2", {"class": "css-dn9ti9-unf-heading-unf-heading e1qvo2ff2"}).text == 0 :
                    continue
            except :
                print(f"Link {self.listtoko[i]} tidak terbuka")
            
            try :
                self.Data.loc[[i],"url"]=self.listtoko[i]
                self.Data.loc[[i],"toko"]=self.soup.find("h1", {"class": "css-1cwp34r"}).text
                self.Data.loc[[i],"awal_buka"]=self.soup.find("p", {"class": "css-2in2o4-unf-heading-unf-heading e1qvo2ff8"}).next_element
                self.Data.loc[[i],"kd_daerah"]=self.kode_kota
                self.Data.loc[[i],"kd_page"]=self.page
                try :
                    self.Data.loc[[i],"alamat"]=self.soup.find("p", {"class": "css-esf63i-unf-heading-unf-heading e1qvo2ff8"}).text
                except :
                    self.Data.loc[[i],"alamat"]=''
                self.Data.loc[[i],"desc"]=self.soup.find("p", {"class": "css-1fe13z7-unf-heading-unf-heading e1qvo2ff8"}).next_element.text
                self.Data.loc[[i],"transaksi"]=self.soup.find("h2", {"class": "css-dn9ti9-unf-heading-unf-heading e1qvo2ff2"}).text
                self.Data.loc[[i],"rating"]=self.soup.find("h2", {"class": "css-3dui13-unf-heading-unf-heading e1qvo2ff2"}).text
                self.Data.loc[[i],"daerah"]=self.soup.find("p", {"class": "css-larfgg-unf-heading-unf-heading e1qvo2ff8"}).next_element.next_element.text
                self.Data.loc[[i],"nomorhp"]=self.Data['desc'].str.findall(r'[0-9]\d{9,115}\S')
                self.Data.loc[[i],"tgl_Scrapping"]=date.today().strftime("%d/%m/%Y")
                self.a=[]
                for j in self.soup.find_all("h5", {"class": "css-1k06g3l-unf-heading-unf-heading e1qvo2ff5"}) :
                    self.a.append(j.text)
                self.layanan=[]
                self.layanan.append(','.join(self.a))
                self.Data.loc[[i],"kurir"]=self.layanan
                print(f"Data link {self.listtoko[i]} berhasil")
            except :
                self.Listunscrapped=[]
                self.Listunscrapped.append(self.listtoko[i])
                print(f"------------------{self.listtoko[i]} UNSCRAPPED ------------------")
                self.Data["tgl_Scrapping"]=date.today().strftime("%d/%m/%Y")
                self.dataunscrapped=pd.DataFrame(self.Listunscrapped,columns={"url"})
                self.dataunscrapped["tgl_Scrapping"]=date.today().strftime("%d/%m/%Y")   


# In[4]:


#Example, we want to pick jakarta Barat with code 174, and page 1
c=Scrape("Object1")
city = 174
page=1
c.GetLink(city,page)
c.GetTokofile()

