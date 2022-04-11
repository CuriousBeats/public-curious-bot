# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 23:04:17 2021

@author: Curious Beats
"""
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import os

def followcount(url,platform):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    options.binary_location = os.environ.get("GOOGLE_CHROME_BIN")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=0,0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extentions")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("start-maximized")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--disable-gpu")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")


    driver = webdriver.Chrome(options=options, executable_path=os.environ.get("CHROMEDRIVER_PATH"))
    if platform == 0:
        if 'm.' in url:
            url = re.sub('m\.', 'www.', url)
        else:
            element = 'div.z-list.mystories'
    elif platform == 1:
        element = 'dd.kudos'
        if '/works' not in url:
            url += '/works'

    elif platform == 2:
        element = 'span.vote-count'
        chaps = 'span.part-count'

    driver.get(url)
    soup = BeautifulSoup(driver.page_source, "lxml")
    if platform == 2:
        soup = soup.find('div', id="works-item-view")
    list_header = []

    header = soup.select(element)
    if platform == 2:
        list_chapters = []
        chap_header = soup.select(chaps)
        for items in chap_header:
            chapters = items.get_text().split()
            list_chapters.append(chapters[0])
    if platform == 1:
        nextpage = soup.select_one('ol.pagination.actions')
        if nextpage != None:

            nextpage = [i for i in nextpage if i != ' ']
            pages = len(nextpage) - 2
            for p in range(pages):
                p += 1
                newurl = url + f'?page={p}'
                driver.get(newurl)
                soup = BeautifulSoup(driver.page_source, "lxml")
                header = soup.select(element)
                for items in header:
                    follows = items.get_text()
                    list_header.append(follows)
    for items in header:
        try:
            if platform == 1 and nextpage == None:
                follows = items.get_text()
                list_header.append(follows)
            elif platform != 1:
                if platform == 2:
                    follows = items.get_text().split()
                    list_header.append(follows[0])
                else:
                    follows = items.get_text().split()
                    if 'Complete' in follows:
                        list_header.append(follows[follows.index('Favs:') + 1])
                    else:
                        list_header.append(follows[follows.index('Follows:') + 1])
        except:
            continue

    driver.quit()

    if platform == 2:
        list_header = [re.sub('K','000',_) for _ in list_header]
        list = [re.sub('\.', '', _) for _ in list_header]
        for i in range(0,len(list_chapters)):
            list_chapters[i] = int(list_chapters[i])
        totalchapters = sum(list_chapters)

    else:
        list = [re.sub(',', '', _) for _ in list_header]

    for i in range(0, len(list)):
        list[i] = int(list[i])

    totalfollows = sum(list)

    if platform == 2:
        average = totalfollows//totalchapters
        return average*len(list)
    else:
        return totalfollows
