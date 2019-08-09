from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import pandas as pd
from lxml import html
import time
from selenium.webdriver.common.keys import Keys
import pandas as pd 
import re

driver = webdriver.Firefox() 

class AHScraper:

    def __init__(self, urlinput):
        self.drv = driver
        self.drv.implicitly_wait(30)
        self.sleep = time.sleep(2)
        self.url = urlinput
    
    def navigateTo(self):
        self.drv.get(self.url)
  
    def getProductLink(self):
        alllinks = self.drv.find_elements_by_tag_name('a')
        links = [alllinks[0].get_attribute('href')]
        for x in range(1, len(alllinks)):
            links.append(alllinks[x].get_attribute('href'))
        links = [x for x in links if re.match(r'(.*?/wi[0-9]{3,9}.*)',x)]
        links = list(dict.fromkeys(links))        

        return links
    
    def searchField(self, searchitem):
        self.drv.find_elements_by_css_selector('#query')[0].send_keys(searchitem)
        self.drv.find_elements_by_css_selector('.button')[0].click()

    





str.extract('(.*?/wi[0-9]{3,9}.*)')
'https://www.ah.nl/producten2'



  


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