import gc
import time
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from scraper import get_chrome_options
from sql_dao.sql_utils import insert_work_score


platform = '烂番茄'


def scrap_score(workId, keyword):
    chrome_options = get_chrome_options()
    web = Chrome(options=chrome_options)
    web.get("https://www.rottentomatoes.com")
    time.sleep(3)
    work_score = get_audience_score(web, keyword)
    if work_score is None:
        web.quit()
        return False
    work_score = round(float(work_score), 1)
    print(work_score)
    success = insert_work_score(workId, work_score, platform)
    time.sleep(1)
    web.quit()  # 退出浏览器
    gc.collect()
    return success


# 搜索电影 获取电影链接
def movie_search(web, keyword):
    web.get("https://www.rottentomatoes.com/search?search={}".format(keyword))
    try:
        lis = web.find_elements(By.XPATH, './/search-page-media-row[@data-qa="data-row"]')
        if not lis:
            return None
        else:
            first_li = lis[0]
            aLink = first_li.find_element(By.XPATH, './/a[@data-qa="info-name"]').get_attribute("href")
            print(aLink)
            return aLink
    except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
        print(e)
        return None


# 获取评分
def get_audience_score(web, keyword):
    url = movie_search(web, keyword)
    if url:
        web.get(url)
        time.sleep(5)
        #  获取分数详情卡片上的评分
        try:
            detail_score = web.find_element(By.XPATH, '//score-details-audience[@slot="audience"]')\
                .get_attribute("averagerating")
        except exceptions.NoSuchElementException:
            print("没有评分")
            detail_score = 0
        return detail_score
    else:
        print("无相关电影")
        return None


if __name__ == '__main__':
    scrap_score(4, "the wandering earth ii")
