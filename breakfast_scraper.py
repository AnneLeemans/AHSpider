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

def load_odata_filter(filter_table, to_filter, filter_column):
    filter_string = ('%27%20or%20'+ to_filter + '%20eq%20%27').join(filter_table[str.lower(filter_column)])

    return filter_string 


# scraper defenitions
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

    return df


def create_search_fields(table): 
    df = table.drop_duplicates(subset = 'ahsearch')
    df['urls'] = 'urls'
    df = df[['ahsearch', 'urls']]
    df.reset_index(inplace=True)
    df.drop(columns = 'index', inplace = True)

    return df



def open_connection():
    drv = webdriver.Firefox()  # op webdriver
    drv.implicitly_wait(30)

    return drv


def get_product_urls(table):
    driver = open_connection()
    for x in range(0,len(table)):
        try:
            driver.get('https://www.ah.nl/zoeken?query='+ table['ahsearch'][x])
            time.sleep(0.5)
            alllinks = driver.find_elements_by_tag_name("a")
            table['urls'][x] = '; '.join(pd.DataFrame(alllinks)[0].apply(lambda x: x.get_attribute('href')).str.extract('(.*?/wi[0-9]{3,9}.*)').\
                dropna().\
                    drop_duplicates()[0])

        except:
            print(table['ahsearch'][x] + ' can"t find product on AH site') 

    return table


def clean_urls_for_scraper(table):
    df = table.copy()

    df = pd.concat([table, df['urls'].str.split(pat = '; ', expand = True)], axis = 1)
    df = df.iloc[:,0:5]
    df2 =  pd.concat([df.iloc[:,0], df.iloc[:,2]], axis = 1).rename(columns={0: 'url'})\
        .append(pd.concat([df.iloc[:,0:1], df.iloc[:,3]], axis = 1).rename(columns={1: 'url'}))\
            .append(pd.concat([df.iloc[:,0:1], df.iloc[:,4]], axis = 1).rename(columns={2: 'url'}))
    df2.sort_values(by='ahsearch', inplace = True)
    df2 = df2[df2['url'].str.contains('ah.nl', na=False)]
    df2 = df2[~df2['url'].isnull()]
    df2.index = list(range(0,len(df2)))

    return df2


def product_info_to_dataframe(df):
    df['title'] = 'product not found'
    df['ahprice'] = 'product not found'
    df['portiegrote'] = 'product not found'
    df['ahsku'] = 'product not found'

    for x in range(0, len(df)):
        try:
            content = requests.get(df['url'][x])
            tree = html.fromstring(content.text)
            df['title'][x] = \
                tree.xpath('//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[1]/h1/span//text()')[0]
            df['ahprice'][x] = \
                tree.xpath('//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[2]/div[1]/div/span[1]//text()')[
                    0] + ',' + \
                tree.xpath(
                    '//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[2]/div[1]/div/span[3]//text()')[
                    0]
            df['portiegrote'][x] = \
                tree.xpath('//*[@id="app"]/article/div[3]/div/div[1]/div[1]/div[1]/div[2]/p//text()')[0]
            df['ahsku'][x] = \
                tree.xpath('//*[@id="app"]/article/div[3]/div/div[2]/div/p/text()')[0]
        except:
            print('product not found')

    df.sort_values('ahprice', ascending=True, inplace = True)
    df.drop_duplicates(subset = 'ahsearch', keep = 'first', inplace = True)

    return df



def get_ah_hf_products(table):    
    search_skus = create_search_fields(table)
    product_urls = get_product_urls(search_skus)
    clean_product_urls = clean_urls_for_scraper(product_urls)
    ah_products = product_info_to_dataframe(clean_product_urls)    
    merge_df = hf_skus.merge(ah_products, how = 'left', left_on = 'ahsearch', right_on = 'ahsearch')

    return merge_df

    # run scraper


# get value per size
def load_sku_info(table):
    sku_filter = '%27' + load_odata_filter(table.iloc[0:100,], 'Code', 'skucode') + '%27'
    skus = fc.load_odata_table('sku', 'Code', 'eq', sku_filter, 'Code,PackingSize')
    for x in range(1,math.ceil(len(table)/100)+1):
        sku_filter = '%27' + load_odata_filter(table.iloc[100*x:100*x+100,], 'Code', 'skucode') + '%27'
        df = fc.load_odata_table('sku', 'Code', 'eq', sku_filter, 'Code,PackingSize')
        skus = skus.append(df)
    
    skus.drop_duplicates(subset = 'code', inplace = True)

    return skus

hf_skus = get_sku_for_weeks(51, 52, 'classic-box')
ah_hf_products = get_ah_hf_products(hf_skus)
sku_info = load_sku_info(hf_skus)

ah_sku_url = ah_hf_products[['skucode', 'url']]
ah_sku_url.dropna(inplace = True)

#this is where you want to save all you skus with urls in the data warehouse for later use 




### read skus wih urls to calculate the price for recipes

#### read ah skus for analysis 

# scraper defenitions
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
      
    return df




def product_info_to_dataframe_fin(df):
    df['title'] = 'product not found'
    df['ahprice'] = isnull()
    df['portiegrote'] = 'product not found'

    for x in range(0, len(df)):
        try:
            content = requests.get(df['url'][x])
            tree = html.fromstring(content.text)
            df['title'][x] = \
                tree.xpath('//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[1]/h1/span//text()')[0]
            df['ahprice'][x] = \
                tree.xpath('//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[2]/div[1]/div/span[1]//text()')[
                    0] + ',' + \
                tree.xpath(
                    '//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[2]/div[1]/div/span[3]//text()')[
                    0]
            df['portiegrote'][x] = \
                tree.xpath('//*[@id="app"]/article/div[3]/div/div[1]/div[1]/div[1]/div[2]/p//text()')[0]
        except:
            print('product not found')

    df.sort_values('skucode', ascending=True, inplace = True)
    df.drop_duplicates(subset = 'skucode', keep = 'first', inplace = True)

    return df


ah_sku_url #= read  ah sku urls

week_recipe = load_recipes(51, 52, 'classic-box')
ah_sku_price = product_info_to_dataframe_fin(ah_sku_url)
sku_info = load_sku_info(week_recipe)
sku_info.drop_duplicates(inplace = True)

week_reipce_ah = week_recipe.merge(sku_info, how = 'inner', left_on = 'skucode', right_on = 'code').\
    merge(ah_sku_price, how = 'left', left_on = 'skucode', right_on = 'skucode')


week_reipce_ah['unit_type'] = week_reipce_ah['skuname'].str.extract('(st\)|g\))')
week_reipce_ah['unit_type'] = week_reipce_ah['unit_type'].str.replace(')','')
week_reipce_ah['unit_type_ah'] = week_reipce_ah['portiegrote'].str.extract('([A-z]{1,40})')
week_reipce_ah['portiegrote'] = week_reipce_ah['portiegrote'].str.extract('([0-9]{1,40})')
week_reipce_ah['portiegrote_ah'] = week_reipce_ah['unit_type_ah'].apply(lambda x: 1000 if x == 'Kilogram' else 1)\
    * week_reipce_ah['portiegrote'].map(int, na_action='ignore')
week_reipce_ah['unit_type_ah'] = week_reipce_ah['unit_type_ah'].apply(lambda x: 'st' if (x == 'Stuks' or x == 'Stuk') else 'g') 
week_reipce_ah['ahprice'] =  week_reipce_ah['ahprice'].str.replace(',', '.')
week_reipce_ah['ahprice'] =  week_reipce_ah['ahprice'].apply(lambda x: np.nan if x == 'product not found' else x)

week_reipce_ah['ah_price'] =  np.where(week_reipce_ah['unit_type'] == week_reipce_ah['unit_type_ah'],
                             round(week_reipce_ah['ahprice'].map(float, na_action='ignore') / \
                                 week_reipce_ah['portiegrote_ah'].map(float, na_action='ignore') * \
                                     week_reipce_ah['packingsize'].map(float, na_action='ignore'),2),np.nan)



week_reipce_ah['cost1pah'] = week_reipce_ah['ah_price'].map(float) * week_reipce_ah['quantitytoorder1p'].map(float)
week_reipce_ah['cost2pah'] = week_reipce_ah['ah_price'].map(float) * week_reipce_ah['quantitytoorder2p'].map(float)
week_reipce_ah['cost3pah'] = week_reipce_ah['ah_price'].map(float) * week_reipce_ah['quantitytoorder3p'].map(float)
week_reipce_ah['cost4pah'] = week_reipce_ah['ah_price'].map(float) * week_reipce_ah['quantitytoorder4p'].map(float)

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

ah_products.to_csv(  # write OT
            'C:/Users/anne.leemans/VSC/AHSpider/ah_ontbijt.csv', sep=';', header=True,
            index=False, encoding='utf-8')


print(math.ceil(4.2))