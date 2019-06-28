from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import html
import time
from tkinter import *


class firstClass:

    def __init__(self):
        self.root = Tk()
        self.root.lift()
        self.root.wm_title('AH Scraper')
        self.root.geometry('400x150+470+350')

        self.topFrame = Frame(self.root)
        self.topFrame.pack(side = TOP)

        self.bottomFrame = Frame(self.root)
        self.bottomFrame.pack(side = BOTTOM)

        self.dropdownTitle = StringVar(self.root)       
        self.dropdownTitle.set('AH Category')
        
        self.dropDown = OptionMenu(self.bottomFrame, self.dropdownTitle, 'agf',
                                                'kant_klaar',
                                                'protein',
                                                'kaas_vlees',
                                                'zuivel',
                                                'bakkerij',
                                                'ontbijt',
                                                'frisdrank',
                                                'wijn',
                                                'bier',
                                                'pasta_rijst',
                                                'conserve',
                                                'snoep_chips',
                                                'diepvries',
                                                'drogist',
                                                'bewuste_voeding',
                                                'huishouden',
                                                'non_food')
        self.dropDown.config(font=("Verdana", 11))
        self.dropDown.grid(row=10,column=0,sticky='nsew',)                                        
        self.dropDown.pack(side = LEFT)
        self.dropDown.focus_set()

        self.showDropdown = Label(self.topFrame, text= 'Albert Heijn scraper choose your category\n', 
            font = ('Veranda', 14))
        self.showDropdown.pack(side = TOP)

        self.printButton = Button(self.bottomFrame, text = '\nStart Scraper\n', command = self.printMessage,\
            font = ('Veranda', 11), bg = 'ivory')
        self.printButton.pack(fill = Y, side = LEFT)


    def printMessage(self):
        self.outputMessage = self.dropdownTitle.get()
        self.root.destroy()

    def waitForInput(self):
        self.root.mainloop()

    def getString(self):
        return self.outputMessage

    def quitApplication(self):
        self.outputMessage = 'Application quit without results'
        self.root.destroy()
    

def getDropdownValue():
    output = firstClass()
    output.waitForInput()
    return output.getString()





# ------- Create defenitions for scraper -------
# list product urls
def ah_product_group(table):
    extensions = {'agf': 'https://www.ah.nl/producten/aardappel-groente-fruit',
                  'kant_klaar': 'https://www.ah.nl/producten/verse-kant-en-klaar-maaltijden-salades',
                  'protein': 'https://www.ah.nl/producten/vlees-kip-vis-vega',
                  'kaas_vlees': 'https://www.ah.nl/producten/kaas-vleeswaren-delicatessen',
                  'zuivel': 'https://www.ah.nl/producten/zuivel-eieren',
                  'bakkerij': 'https://www.ah.nl/producten/bakkerij',
                  'ontbijt': 'https://www.ah.nl/producten/ontbijtgranen-broodbeleg-tussendoor',
                  'frisdrank': 'https://www.ah.nl/producten/frisdrank-sappen-koffie-thee',
                  'wijn': 'https://www.ah.nl/producten/wijn',
                  'bier': 'https://www.ah.nl/producten/bier-sterke-drank-aperitieven',
                  'pasta_rijst': 'https://www.ah.nl/producten/pasta-rijst-internationale-keuken',
                  'conserve': 'https://www.ah.nl/producten/soepen-conserven-sauzen-smaakmakers',
                  'snoep_chips': 'https://www.ah.nl/producten/snoep-koek-chips',
                  'diepvries': 'https://www.ah.nl/producten/diepvries',
                  'drogist': 'https://www.ah.nl/producten/drogisterij-baby',
                  'bewuste_voeding': 'https://www.ah.nl/producten/bewuste-voeding',
                  'huishouden': 'https://www.ah.nl/producten/huishouden-huisdier',
                  'non_food': ' https://www.ah.nl/producten/koken-tafelen-non-food'
                  }
    extension = extensions[table]
    return extension


def navigate_to_url(url):
    drv = webdriver.Firefox()  # op webdriver
    drv.implicitly_wait(30)
    drv.get(url)

    return drv


def get_all_links(drv):
    alllinks = drv.find_elements_by_tag_name("a")
    links = [alllinks[0].get_attribute('href')]
    for x in range(1, len(alllinks)):
        links.append(alllinks[x].get_attribute('href'))

    return links


def clean_data_for_scrape(drv):
    ah_urls = get_all_links(drv)
    ahurls_df = pd.DataFrame(ah_urls)
    ahurls_df['url'] = ahurls_df[0].str.extract('(.*?ah.nl/producten/.*)')
    ahurls_df['remove'] = ahurls_df['url'].str.count('/')
    ahurls_df = ahurls_df[ahurls_df['remove'] == 4]
    ahurls_df['remove'] = ahurls_df['url'].str.extract('(brandAlphabet|eerder-gekocht|merk)')
    ahurls_df = ahurls_df[pd.isnull(ahurls_df['remove'])]
    urls = ahurls_df['url'].tolist()

    return urls


def get_page_with_products(drv, url, x):
    driver.get(url[x])
    driver.implicitly_wait(30)
    time.sleep(2)
    product_link = get_all_links(drv)
    product_link_df = pd.DataFrame(product_link)
    product_link_df['url'] = product_link_df[0].str.extract('(.*' + url[x] + '.*)')
    product_link_df = product_link_df.dropna()
    product_link_df.drop_duplicates(subset='url', inplace=True)
    product_link_df['remove'] = product_link_df['url'].str.extract('(kenmerk=|bonus)')
    product_link_df = product_link_df[pd.isnull(product_link_df['remove'])]
    products_urls_fin = product_link_df['url'].tolist()

    return products_urls_fin


def load_pages(drv, url):
    list = []
    for x in range(0, len(url)):
        try:
            temp_list = get_page_with_products(drv, url, x)
            list = list + temp_list
        except:
            print('line ' + str(x) + ' skipped: ' + url[x])

    return list


def get_product_urls(url, x):
    driver.get(url[x])
    driver.implicitly_wait(30)
    time.sleep(2)
    fin_product_url = get_all_links(driver)
    fin_product_url = pd.DataFrame(fin_product_url)
    fin_product_url['url'] = fin_product_url[0].str.extract('(.*?/wi[0-9]{3,9}.*)')
    fin_product_url = fin_product_url.dropna()
    fin_product_url.drop_duplicates(subset='url', inplace=True)
    fin_product_url = fin_product_url['url'].tolist()

    return fin_product_url


def get_final_product_urls(string):
    list_fin_product_url = []
    for x in range(0, len(string)):
        try:
            temp_list = get_product_urls(string, x)
            list_fin_product_url = list_fin_product_url + temp_list
        except:
            print('line ' + str(x) + ' skipped: ' + string[x])

    return list_fin_product_url


def product_info_to_dataframe(urls):
    df = pd.DataFrame(urls)
    df.drop_duplicates(subset=0, inplace=True)
    df['title'] = 'product not found'
    df['price'] = 'product not found'
    df['portiegrote'] = 'product not found'
    df['ahsku'] = 'product not found'

    for x in range(0, len(df)):
        try:
            content = requests.get(df[0][x])
            tree = html.fromstring(content.text)
            df['title'][x] = \
                tree.xpath('//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[1]/h1/span//text()')[0]
            df['price'][x] = \
                tree.xpath(
                    '//*[@id="app"]/article/div[2]/div/div/div/article/div/div/div[2]/div[2]/div[1]/div/span[1]//text()')[
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

    return df



# --------------------------------------------- Run AH scraper ---------------------------------------------------------

def runScraper():
    cat = getDropdownValue()
    driver = navigate_to_url("https://www.ah.nl/producten")
    time.sleep(3)

    # get links where products are located
    list_sub_cat = load_pages(driver, [ah_product_group(cat)])
    list_sub_sub_cat = load_pages(driver, list_sub_cat)
    list_sub_sub__sub_cat = load_pages(driver, list_sub_sub_cat)

    # create list with all urls
    final_url_forproduct_search = list_sub_cat + list_sub_sub_cat + list_sub_sub__sub_cat
    final_url_forproduct_search =  list(dict.fromkeys(final_url_forproduct_search))

    # get urls of products
    final_product_urls = get_final_product_urls(final_url_forproduct_search)

    # get product info
    ah_products = product_info_to_dataframe(final_product_urls)

    return ah_products

# to disc
ah_products.to_csv('G:/My Drive/NL - 15 - Procurement/Persoonlijk/Anne/Tools/Scraper/ah_products.csv', sep = ';', header = True, index = False)

