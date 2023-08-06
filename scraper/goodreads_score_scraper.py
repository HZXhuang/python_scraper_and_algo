import gc
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import exceptions
from scraper import get_chrome_options
from sql_dao.sql_utils import insert_work_score

platform = 'GoodReads'


def scrap_score(workId, keyword):
    chrome_options = get_chrome_options()
    web = Chrome(options=chrome_options)
    web.get("https://www.goodreads.com/search?utf8=%E2%9C%93&query={}".format(keyword))
    time.sleep(3)
    score = get_score(web)
    score = round(float(score), 1)
    # print(score)
    success = insert_work_score(workId, score, platform)
    time.sleep(1)
    web.quit()
    gc.collect()
    return success


#  监听某个元素的出现
def get_element_by_xpath(driver, xpath_pattern):
    return WebDriverWait(driver, 20, 1)\
        .until(EC.presence_of_element_located((By.XPATH, xpath_pattern)))


#  搜索作品 返回作品链接
def search_work(web):
    try:
        trs = web.find_elements(By.XPATH, '//tr[@itemtype="http://schema.org/Book"]')
        if not trs:
            return None
        else:
            first_tr = trs[0]
            first_tr_td = first_tr.find_element(By.XPATH, './/td[@width="5%"]')
            book_url = first_tr_td.find_element(By.XPATH, './/a').get_attribute("href")
            # print(book_url)
            return book_url
    except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
        print(e)
        return None


#  获取作品评分
def get_score(web):
    book_url = search_work(web)
    if book_url:
        web.get(book_url)
        try:
            close_btn = get_element_by_xpath(web, '//button[@aria-label="Close"]')
            close_btn.click()  # 关闭弹出来的窗口
            time.sleep(2)
        except exceptions.TimeoutException as e:
            print(e)
        time.sleep(8)
        try:
            rating_div = web.find_element(By.XPATH, '//div[@class="BookPageMetadataSection__ratingStats"]')
            work_score = rating_div.find_element(By.XPATH, './/div[@class="RatingStatistics__rating"]').text
        except exceptions.NoSuchElementException:
            print("没有评分")
            work_score = 0
        return work_score
    else:
        print("无相关作品书籍")
        return None


if __name__ == '__main__':
    scrap_score(18, "舌尖上的中国（第1季）")

