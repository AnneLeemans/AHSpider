##### LOAD PACKAGES
import sys
sys.path.insert(1, 'C:/Users/anne.leemans/VSC/Defenitions')
import defenitions as fc
import os
import pandas as pd
from selenium import webdriver
from lxml import html
import requests
import time
import math
import numpy as np
import requests as requests
from urllib.parse import urlparse as urlparse
from xml.etree import ElementTree as ElementTree
from appiepy import Product
from pprint import pprint
import re
import time
import tkinter as tk
from tkinter import *
from tkinter import messagebox

##### INPUT DEFENITION
class takeInput(object):

    def __init__(self, prdorsup):
        self.root = Tk()
        self.root.lift()
        self.root.wm_title("Ah Scraper")
        self.root.geometry('480x220+670+400')
        self.string = ''
        self.acceptInput(prdorsup)

    def acceptInput(self, prdorsup):
        r = self.root
        Label(r, text="", font=("Verdana", 16), fg="Green").grid(row=0)

        Label(r, text="  Start week      ", font=("Verdana", 16), fg="Green").grid(row=1)
        self.startWeek = Entry(r, text='strt', font=('Verdana', 16))
        self.startWeek.grid(row=1, column=1)

        Label(r, text="  End week        ", font=("Verdana", 16), fg="Green").grid(row=2)
        self.endWeek = Entry(r, text='end', font=('Verdana', 16))
        self.endWeek.grid(row=2, column=1)

        Label(r, text="  "+prdorsup+" ", font=("Verdana", 16), fg="Green").grid(row=3)
        self.nameInput = Entry(r, text='inputtxt', font=('Verdana', 16))
        self.nameInput.grid(row=3, column=1)

        Label(r, text="", font=("Verdana", 16), fg="Green").grid(row=4)

        self.buttonEnd = Button(r, text='Generate Output', command=self.gettext, font=("Verdana", 16), fg="#f0f6da", bg='green')
        self.buttonEnd.grid(row=5, column=1)

        Label(r, text="", font=("Verdana", 16), fg="Green").grid(row=6)
    
    def gettext(self):
        self.string1 = self.startWeek.get()
        self.string2 = self.endWeek.get()
        self.string3 = self.nameInput.get()
        self.root.lift()
        self.root.destroy()

    def getString(self):
        return self.string1, self.string2, self.string3

    def waitForInput(self):
        self.root.mainloop()


def getText(prdorsup):
    msgBox = takeInput(prdorsup)
    # loop until the user makes a decision and the window is destroyed
    msgBox.waitForInput()
    return msgBox.getString()



##### CREATE FILTER FOR SKUS SPECIFIC WEEKS
def load_odata_filter(filter_table, to_filter, filter_column):
    filter_string = ('%27%20or%20'+ to_filter + '%20eq%20%27').join(filter_table[str.lower(filter_column)])

    return filter_string 


##### LOAD & CLEAN DATA FOR SCRAPER 
def get_sku_for_weeks(strtWeek, endWeek, productFamily):
    df = pd.DataFrame(index = [], columns = ['price', 'product', 'skucode', 'skuname'])
    for x in range(strtWeek, endWeek):
        df2 = fc.load_odata_table('recipesku', 'COGSDetailSKU_Week', 'eq', \
            fc.get_boxweek_id(x), 'ID,Price,Product,SKUCode,SKUName,Region,QuantityToOrder2P') #,RecipeCode,Slot
        df2 = df2[df2['product'] == productFamily]
        df2 = df2[df2['quantitytoorder2p']!=0]
        df2 = df2[df2['region'] == 'NL']
        df = df.append(df2)
    df.drop_duplicates(subset='skucode', inplace = True)

    df['ahsearch'] = df['skuname'].str.lower()
    df['ahsearch'] = df['ahsearch'].str.replace('\(.*', '')
    df['ahsearch'] = df['ahsearch'].str.strip()
    df['ahsearch'] = df['ahsearch'].str.replace(' ', '%20')
    df.reset_index(inplace=True)

    # Drop duplicate urls
    df2 = df[['region', 'ahsearch']]
    df2 = df[['region', 'ahsearch']].drop_duplicates()
    df2.reset_index(inplace = True)
    df2.drop('index', axis = 1, inplace = True)

    return df, df2


##### OPEN SELENIUM CONNECTION
def open_connection():
    drv = webdriver.Firefox()  # op webdriver
    drv.implicitly_wait(30)

    return drv


##### LOAD AH URLS
def get_product_urls(table):      
    driver = open_connection()
    table['url'] = ''
    for x in range(0,len(table)):
        try:
            driver.get('https://www.ah.nl/zoeken?query='+ table['ahsearch'][x])
            time.sleep(0.5)
            check = driver.find_element_by_xpath('//*[@id="app"]').text
            if re.findall('geen resultaten', check) == ['geen resultaten']:
                table['url'][x] = 'product not found!'
            else:
                alllinks = driver.find_elements_by_tag_name("a")
                table['url'][x] = '; '.join(pd.DataFrame(alllinks)[0].\
                    apply(lambda x: x.get_attribute('href')).str.extract('(.*?/wi[0-9]{3,9}.*)').\
                        dropna().drop_duplicates()[0])       
        except:
            print('Can"t find product on AH site') 

    return table


#### CONCATE MULTIPLE URL RESULTS
def clean_urls_for_scraper(table):
    df = table.copy()

    df = pd.concat([table, df['url'].str.split(pat = '; ', expand = True)], axis = 1)
    df = df.iloc[:,1:7]
    df2 =  pd.concat([df.iloc[:,0], df.iloc[:,2]], axis = 1).rename(columns={0: 'url'})\
        .append(pd.concat([df.iloc[:,0:1], df.iloc[:,3]], axis = 1).rename(columns={1: 'url'}))\
            .append(pd.concat([df.iloc[:,0:1], df.iloc[:,4]], axis = 1).rename(columns={2: 'url'}))\
                .append(pd.concat([df.iloc[:,0:1], df.iloc[:,5]], axis = 1).rename(columns={3: 'url'}))

    df2.sort_values(by='ahsearch', inplace = True)
    df2 = df2[df2['url'].str.contains('ah.nl', na=False)]
    df2 = df2[~df2['url'].isnull()]
    df2.reset_index(inplace = True)
    df2.drop('index', axis = 1, inplace = True)
    df2['title'] = ''
    df2['category']  = ''
    df2['ah_price']  = ''
    df2['size']  = ''
    df2['size_type']  = ''
    df2['size_nr']  = ''
    df2['price_100(g/l)_p1st'] = ''
    df2['ahid']  = ''

    return df2


##### LOAD PRODUCT INFO
def load_product_info(table):
    for x in range(0,len(table)):
        try:
            product = vars(Product(table['url'][x]))
            table['title'][x] = product['description']
            table['category'][x] = product['category']
            table['ah_price'][x] = float(product['price_current'])
            table['size'][x] = product['unit_size']
            table['size_type'][x] = re.findall('(kg|ml|st|l|g)', table['size'][x])[0]
            table['size_nr'][x] = float(re.findall(r'([0-9]{1,4}(\\.|,)[0-9]{1,3}|[0-9]{1,4})', table['size'][x])[0][0].replace(',', '.'))
            if (table['size_type'][x] == 'kg' or table['size_type'][x] == 'l'): 
                table['price_100(g/l)_p1st'][x] = round((table['ah_price'][x]/(table['size_nr'][x]*1000))*100,2)
            elif (table['size_type'][x] == 'st'):
                table['price_100(g/l)_p1st'][x] = round(table['ah_price'][x]/(table['size_nr'][x]),2)
            else:          
                table['price_100(g/l)_p1st'][x] = round((table['ah_price'][x]/table['size_nr'][x])*100,2)
            table['ahid'][x] = product['id']

        except:
            print('product info not found')
    # litte cleaning
    table['size_nr'] = np.where(table['size'] == 'per stuk', \
        1, table['size_nr'])
    table['price_100(g/l)_p1st'] = np.where(table['size'] == 'per stuk', \
        1*table['ah_price'], table['price_100(g/l)_p1st'])
    return table


##### LOAD DATA FOR SEARCH
def load_ah_data():
    inputs = getText('Product Group')
    meta_data = get_sku_for_weeks(int(inputs[0]), int(inputs[1]), inputs[2])
    hf_skus_for_merge = meta_data[0]
    hf_skus_for_search = meta_data[1]
    hf_ah_urls = get_product_urls(hf_skus_for_search)
    hf_ah_clean_urls = clean_urls_for_scraper(hf_ah_urls)
    hf_ah_product_info = load_product_info(hf_ah_clean_urls)

    ##### PRODUCTS READY FOR ANALYSIS
    hf_products_ready_for_analysis = hf_skus_for_merge.merge(hf_ah_product_info, how = 'outer', left_on = 'ahsearch', right_on = 'ahsearch')
    hf_products_ready_for_analysis.drop('index', axis = 1, inplace = True)
    hf_products_ready_for_analysis.to_csv('productsW40-41.csv', sep = ';', header = True, index = False, encoding = 'utf-8-sig')


