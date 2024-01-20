import re
import time

import pandas as pd
import requests
import json
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from sql_dao.sql_utils import insert_work


# 使用requests按页获取电影信息 返回电影链接
def get_movie_href(start_page):
    page_size = 30
    url = "https://movie.douban.com/j/search_subjects?type=movie&tag=%E5%8D%8E%E8%AF%AD&sort=recommend&page_limit={}&page_start={}".format(page_size, start_page*page_size)
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36 Edg/116.0.1938.76"}
    response = requests.get(url,  headers=header)
    html_str = response.text
    # 得到的数据直接是json数据，所以直接处理
    data = json.loads(html_str)
    # 返回列表数据
    movieList = data["subjects"]
    link_list = []
    for movie in movieList:
        link_list.append(movie['url'])
    return link_list


def create_driver_instance():
    web = Chrome()
    web.get("https://movie.douban.com/")
    return web


#使用selenium获取电影类型、简介等信息
def get_movie_message(web, hrefList):
    time.sleep(1)
    category = "影视"
    for href in hrefList:
        web.get(href)
        labelList = []
        name = web.find_element(By.XPATH, '//span[@property="v:itemreviewed"]').text
        imgUrl = web.find_element(By.XPATH, '//img[@rel="v:image"]').get_attribute("src")
        labelElems = web.find_elements(By.XPATH, '//span[@property="v:genre"]')
        briefIntro = web.find_element(By.XPATH, '//span[@property="v:summary"]').text
        releaseTime = web.find_element(By.XPATH, '//span[@property="v:initialReleaseDate"]').text
        releaseTime = str(pd.to_datetime(re.sub('\\((.*?)\\)', '', releaseTime)).date())
        for label in labelElems:
            labelList.append(label.text)
        labelStr = " ".join(labelList)
        insert_work(name, category, labelStr, href, imgUrl, briefIntro, releaseTime)
        # print(name, category, labelStr, href, imgUrl, briefIntro, releaseTime)
        time.sleep(1)


#根据页数获取电影
def get_movie_byPage(web, pageNum):
    aLinks = []
    for page in range(1, 1 + pageNum):
        linkList = get_movie_href(page)
        aLinks.extend(linkList)
    # print(aLinks)
    web = create_driver_instance()
    get_movie_message(web, aLinks)


#获取中国文学作品
def get_literature(web, page_num):
    for i in range(page_num):
        web.get("https://book.douban.com/tag/%E4%B8%AD%E5%9B%BD%E6%96%87%E5%AD%A6?start={}&type=T".format(i*20))
        li_List = web.find_elements(By.XPATH, '//li[@class="subject-item"]')
        category = "书籍"
        for li in li_List:
            workUrl = li.find_element(By.XPATH, './div[1]/a').get_attribute("href")
            name = li.find_element(By.XPATH, './div[2]/h2/a').text
            imgUrl = li.find_element(By.XPATH, './div[1]/a/img').get_attribute("src")
            briefIntro = li.find_element(By.XPATH, './div[2]/p').text
            labelStr = ""
            releaseTime = li.find_element(By.XPATH, ".//div[@class='pub']").text.split('/')[2].strip()
            releaseTime = str(pd.to_datetime(releaseTime).date())
            insert_work(name, category, labelStr, workUrl, imgUrl, briefIntro, releaseTime)
            # print(name, category, labelStr, workUrl, imgUrl, briefIntro, releaseTime)


if __name__ == '__main__':
    web = create_driver_instance()
    # get_literature(web, 3)
    get_movie_byPage(web, 2)
    web.close()
    x = set()
    import random
    random.random()

