import gc

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from scraper import get_chrome_options
import time
from sql_dao.sql_utils import insert_work_score


platform = "IMDb"


def scrap_score(workId, keyword):
    driver = webdriver.Chrome(options=get_chrome_options(False))
    driver.get("https://www.imdb.com/find/?s=tt&q={}&ref_=nv_sr_sm".format(keyword))
    time.sleep(5)
    try:
        title = driver.find_element(By.XPATH, '//section[@data-testid="find-results-section-title"]/div[2]/ul/li')
        print(title.text)
    except exceptions.NoSuchElementException:
        print("搜索结果为空")
        return False
    time.sleep(1)
    title.click()

    time.sleep(10)
    try:
        print(driver.current_url)
        score = driver.find_element(By.XPATH, '//div[@data-testid="hero-rating-bar__aggregate-rating__score"]/span')\
            .text.strip()
        print(score)
    except exceptions.NoSuchElementException:
        print("没有评分")
        score = "0"
    if len(score) == 0:
        score = "0"
    score = round(float(score) / 2, 1)
    print(score)
    success = insert_work_score(workId, score, platform)
    time.sleep(1)
    driver.quit()
    gc.collect()
    return success


if __name__ == "__main__":
    print(scrap_score(1, "西游记"))
