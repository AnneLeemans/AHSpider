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
def load_recipes(strtWeek, endWeek, productFamily):
    df = pd.DataFrame(index = [], columns = ['price', 'product', 'skucode', 'skuname', 'region', 'quantitytoorder1p', 
        'quantitytoorder2p', 'quantitytoorder3p', 'quantitytoorder4p','recipecode', 'slot'])

    for x in range(strtWeek, endWeek):
        df2 = fc.load_odata_table('recipesku', 'COGSDetailSKU_Week', 'eq', \
            fc.get_boxweek_id(x), 'Price,Product,SKUCode,SKUName,Region,QuantityToOrder1P,\
                QuantityToOrder2P,QuantityToOrder3P,QuantityToOrder4P,RecipeCode,Slot')
        df = df.append(df2)

    df = df[df['product'] == productFamily]
    df = df[df['region'] == 'NL']
    df['hf_week'] = '2019-W' + str(strtWeek)
    df['cost1p'] = df['price'].map(float) * df['quantitytoorder1p'].map(float)
    df['cost2p'] = df['price'].map(float) * df['quantitytoorder2p'].map(float)
    df['cost3p'] = df['price'].map(float) * df['quantitytoorder3p'].map(float)
    df['cost4p'] = df['price'].map(float) * df['quantitytoorder4p'].map(float)

    df3 = df.copy()
    sku_filter = '%27' + load_odata_filter(df3.iloc[0:100,], 'Code', 'skucode') + '%27'
    skus = fc.load_odata_table('sku', 'Code', 'eq', sku_filter, 'Code,PackingSize')
    for x in range(1,math.ceil(len(df)/100)+1):
        sku_filter = '%27' + load_odata_filter(df3.iloc[100*x:100*x+100,], 'Code', 'skucode') + '%27'
        df4 = fc.load_odata_table('sku', 'Code', 'eq', sku_filter, 'Code,PackingSize')
        skus = skus.append(df4)

    skus.drop_duplicates(subset = 'code', inplace = True)
    df5 = df.merge(skus, left_on = 'skucode', right_on = 'code')

    return df5





##### LOAD PRODUCT INFO
def load_product_info(table):
    table = table[['region','url']].copy()
    table.drop_duplicates(inplace = True)
    table.dropna(inplace = True)
    table.reset_index(inplace = True)
    table.drop('index', axis = 1, inplace = True)
    table['title'] = ''
    table['ah_price']  = ''
    table['size']  = ''
    table['size_type']  = ''
    table['size_nr']  = ''
    table['price_100(g/l)_p1st'] = ''
    table['ahid']  = table['url'].str.extract('(wi[0-9]{1,12})')

    for x in range(0,len(table)):
        try:
            product = vars(Product(table['url'][x]))
            table['title'][x] = product['description']
            table['ah_price'][x] = float(product['price_current'])
            table['size'][x] = product['unit_size']
            table['size_type'][x] = re.findall('(kg|ml|st|l|g)', table['size'][x])[0]
            table['size_nr'][x] = float(re.findall(r'([0-9]{1,4}(\\.|,)[0-9]{1,3}|[0-9]{1,4})', \
                table['size'][x])[0][0].replace(',', '.'))
            if (table['size_type'][x] == 'kg' or table['size_type'][x] == 'l'): 
                table['price_100(g/l)_p1st'][x] = round((table['ah_price'][x]/(table['size_nr'][x]*1000))*100,2)
            elif (table['size_type'][x] == 'st'):
                table['price_100(g/l)_p1st'][x] = round(table['ah_price'][x]/(table['size_nr'][x]),2)
            else:          
                table['price_100(g/l)_p1st'][x] = round((table['ah_price'][x]/table['size_nr'][x])*100,2)

        except:
            print('product info not found')
    
    # litte cleaning
    table['size_nr'] = np.where(table['size'] == 'per stuk', \
        1, table['size_nr'])
    table['price_100(g/l)_p1st'] = np.where(table['size'] == 'per stuk', \
        1*table['ah_price'], table['price_100(g/l)_p1st'])

    return table


hf_sku_info = load_recipes(40, 41, 'classic-box')

## load ah urls from dhw
test_df

## join ah urls with weekly sku codes
hf_skus_ah_urls = hf_sku_info.merge(test_df, how = 'left', left_on = 'skucode', right_on = 'skucode')

## load ah prices
ah_prices = load_product_info(hf_skus_ah_urls)

## join skus with ah prices
hf_skus_ah_prices = hf_skus_ah_urls.merge(ah_prices, how = 'left', left_on = 'url', right_on = 'url')





def create_cost_comparison(table)
week_reipce_ah['unit_type'] = week_reipce_ah['skuname'].str.extract('(st\)|g\)|ml\)|l\))')
week_reipce_ah['unit_type'] = week_reipce_ah['unit_type'].str.replace(')','')
week_reipce_ah['unit_type'] = np.where(week_reipce_ah['unit_type'].isnull(), 'st', week_reipce_ah['unit_type'])
week_reipce_ah['price_100(g/l)_p1st'] = week_reipce_ah['price_100(g/l)_p1st'].str.strip()
test = week_reipce_ah.copy()
test['check'] = test['price_100(g/l)_p1st'].str.extract('([A-z]{1,10})')

week_reipce_ah['cost1pah'] = np.where(week_reipce_ah['unit_type'] != 'st', \
    week_reipce_ah['price_100(g/l)_p1st'].map(float, na_action='ignore') / 100\
         * week_reipce_ah['packingsize'].map(float, na_action='ignore') * week_reipce_ah['quantitytoorder1p'].map(float, na_action='ignore'),\
        week_reipce_ah['price_100(g/l)_p1st'].map(float, na_action='ignore') * week_reipce_ah['packingsize'].map(float, na_action='ignore')\
             * week_reipce_ah['quantitytoorder1p'].map(float, na_action='ignore'))
        
week_reipce_ah['cost2pah'] = week_reipce_ah['price_100(g/l)_p1st'].map(float) * week_reipce_ah['quantitytoorder2p'].map(float)
week_reipce_ah['cost3pah'] = week_reipce_ah['price_100(g/l)_p1st'].map(float) * week_reipce_ah['quantitytoorder3p'].map(float)
week_reipce_ah['cost4pah'] = week_reipce_ah['price_100(g/l)_p1st'].map(float) * week_reipce_ah['quantitytoorder4p'].map(float)

recipe_price = week_reipce_ah[[
        'hf_week',
        'slot',    
        'cost1p',
        'cost2p',
        'cost3p',
        'cost4p',
        'cost1pah',
        'cost2pah',
        'cost3pah',
        'cost4pah']]

recipe_price = recipe_price.groupby(['hf_week', 'slot']).sum()
recipe_price.reset_index(inplace = True)





for x in range(0,len(table)):
    table['size_type'][x] = re.findall('(kg|ml|st|l|g)', table['size'][x])[0]
    table['size_nr'][x] = float(re.findall(r'([0-9]{1,4}(\\.|,)[0-9]{1,3}|[0-9]{1,4})', \
        table['size'][x])[0][0].replace(',', '.'))
    if (table['size_type'][x] == 'kg' or table['size_type'][x] == 'l'): 
        table['price_100(g/l)_p1st'][x] = round((ah_prices['ah_price'][x]/(ah_prices['size_nr'][x]*1000))*100,2)
    elif (table['size_type'][x] == 'st'):
        table['price_100(g/l)_p1st'][x] = round(table['ah_price'][x]/(table['size_nr'][x]),2)
    else:          
        table['price_100(g/l)_p1st'][x] = round((table['ah_price'][x]/table['size_nr'][x])*100,2)
       
            
      