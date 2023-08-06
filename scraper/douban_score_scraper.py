import gc

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import time
from scraper import get_chrome_options
from sql_dao.sql_utils import insert_work_score


platform = "豆瓣"


def scrap_score(workId, keyword):
    chrome_options = get_chrome_options(False)
    web = webdriver.Chrome(options=chrome_options)
    # 根据关键字搜索
    web.get("https://www.douban.com/search?q={}".format(keyword))
    # 选择搜索结果的第一个
    try:
        select = web.find_element(By.XPATH, '//div[@class="title"]//a')
    except exceptions.NoSuchElementException:
        print("搜索结果为空")
        return False
    select.click()
    time.sleep(2)
    windows = web.window_handles
    web.switch_to.window(windows[-1])
    try:
        score = web.find_element(By.XPATH, '//strong[@property="v:average"]').text
    except exceptions.NoSuchElementException:
        print("没有评分")
        score = "0"
    if len(score.strip()) == 0:
        score = "0"
    score = round(float(score)/2, 1)
    print(score)
    success = insert_work_score(workId, score, platform)
    time.sleep(1)
    web.quit()
    gc.collect()
    return success


if __name__ == "__main__":
    scrap_score(2, "流浪地球1")
