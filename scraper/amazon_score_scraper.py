import gc

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
import time
from scraper import get_chrome_options
from sql_dao.sql_utils import insert_work_score

platform = "Amazon"


def scrap_score(workId, keyword):
    chrome_options = get_chrome_options(False)
    search = keyword.replace(" ", "+")
    web = webdriver.Chrome(options=chrome_options)

    web.get("https://www.amazon.com/s?k={}&__mk_zh_CN=亚马逊平台&cried=30S6SEQ3D6Z7&prefix={}&ref=nb_sb_nos_1"
            .format(search, search))
    search_result = web.find_elements(
        By.XPATH,
        '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]'
    )
    while len(search_result) == 0:
        web.refresh()
        time.sleep(1)
        search_result = web.find_elements(
            By.XPATH,
            '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]'
        )
    search_result[0].click()
    time.sleep(1)
    try:
        score = web.find_element(By.XPATH, '//*[@id="acrPopover"]//span[@class="a-size-base a-color-base"]').text
    except exceptions.NoSuchElementException:
        print("没有评分")
        score = "0"
    if len(score.strip()) == 0:
        score = "0"
    score = round(float(score), 1)
    print(score)
    success = insert_work_score(workId, score, platform)
    time.sleep(1)
    web.quit()
    gc.collect()
    return success


if __name__ == "__main__":
    res = scrap_score(1, "the journey to the west")
    print(res)
