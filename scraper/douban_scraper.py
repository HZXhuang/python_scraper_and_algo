from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time
import random
import numpy as np
import pandas as pd
from scraper import base_path, get_chrome_options
from scraper.my_utils import text_clean, parse_date_format, analyze_polarity
from sql_dao.sql_utils import insert_comment

platform = "豆瓣"
country = "中国"


def scrap_reviews(keyword, workId):
    curr_page = 1
    plan_page = 15
    comments = []
    # 把浏览器参数传入到网页驱动
    web = webdriver.Chrome(options=get_chrome_options(False))
    web.get("https://www.douban.com")
    # 找到输入框并填入内容
    search_content = web.find_element(By.XPATH, '//*[@id="anony-nav"]/div[3]/form/span[1]/input')
    search_content.send_keys(keyword)
    time.sleep(1)
    # 进行搜索
    do_search = web.find_element(By.XPATH, '//*[@id="anony-nav"]/div[3]/form/span[2]/input')
    do_search.click()
    # 选择搜索结果的第一个
    select = web.find_element(By.XPATH, '//*[@id="content"]/div/div[1]/div[3]/div/div/div[1]/a')
    select.click()
    time.sleep(1)
    windows = web.window_handles
    web.switch_to.window(windows[-1])
    time.sleep(1)

    js = "window.scrollTo(0, document.body.scrollHeight)"
    web.execute_script(js)

    # 找到更多评论链接并点击
    more_comments = web.find_element(By.XPATH, '//*[@id="reviews-wrapper"]/p/a')
    more_comments.click()
    while curr_page <= plan_page:
        time.sleep(1)
        js = "window.scrollTo(0, document.body.scrollHeight)"
        web.execute_script(js)
        time.sleep(2)
        try:
            comment_wrapper_list = web.find_elements(By.XPATH, '//div[@class="main review-item"]')
        except exceptions.NoSuchElementException:
            print("没有评论列表")
            continue
        for comment_wrapper in comment_wrapper_list:
            try:
                comment = comment_wrapper.find_element_by_xpath('.//div[@class="short-content"]').text\
                    .replace("\n", "").replace("(展开)", "").replace("这篇影评可能有剧透", "")
            except exceptions.NoSuchElementException:
                print("找不到评论")
                continue
            comment = text_clean(comment)
            if len(comment.strip()) == 0:
                print("评论内容为空")
                continue
            try:
                post_time = comment_wrapper.find_element_by_xpath('.//span[@class="main-meta"]').text
            except exceptions.NoSuchElementException:
                print("找不到时间")
                post_time = '2021-03-02'
            post_time = parse_date_format(post_time)
            try:
                likes = comment_wrapper.find_element_by_xpath('.//a[@class="action-btn up"]').text.strip()
                if not likes:
                    likes = str(random.randint(0, 5))
            except exceptions.NoSuchElementException:
                print("没有点赞数")
                likes = str(random.randint(0, 5))
            translated = comment
            sentiment = analyze_polarity(translated)
            comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])
            insert_comment(comment, translated, likes, workId, sentiment, country, platform, post_time)

        # 进入下一个评论页
        time.sleep(2)
        try:
            next_page = web.find_element(By.XPATH, '//span[@class="next"]')
        except exceptions.NoSuchElementException:
            print("没有下一页按钮")
            break
        next_page.click()
        curr_page = curr_page + 1
    if not comments:
        return
    data = np.array(comments)
    df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
                                     'sentiment', 'country', 'platform', 'postTime'])
    df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, encoding='utf-8')
    return True


if __name__ == "__main__":
    scrap_reviews("流浪地球", 4)
