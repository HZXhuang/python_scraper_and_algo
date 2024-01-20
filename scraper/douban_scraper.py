import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time
import random
import json
import numpy as np
import pandas as pd
from scraper import base_path, get_chrome_options
from scraper.my_utils import text_clean, parse_date_format, analyze_polarity, fan_to_jian
from sql_dao.sql_utils import insert_comment, detect_duplicated_comment

platform = "豆瓣"
country = "中国"
optional_country = ["中国", "中国", "加拿大", "中国", "美国", "法国", "美国", "加拿大",
                    "加拿大", "日本", "加拿大", "日本", "韩国", "中国", "英国", "法国", "中国",
                    "俄罗斯", "中国", "加拿大", "美国", "德国", "中国"]
base_url = "https://www.douban.com/search"


def scrap_reviews(keyword, workId, categoryId):

    comments = []
    # 把浏览器参数传入到网页驱动
    web = webdriver.Chrome(options=get_chrome_options(False))
    search_url = "{}?cat={}&q={}".format(base_url, categoryId, keyword)
    web.get(search_url)
    check_login(web)
    web.get(search_url)
    time.sleep(4)
    # web.get("https://www.douban.com")
    # # 找到输入框并填入内容
    # search_content = web.find_element(By.XPATH, '//*[@id="anony-nav"]/div[3]/form/span[1]/input')
    # search_content.send_keys(keyword)
    # time.sleep(1)
    # # 进行搜索
    # do_search = web.find_element(By.XPATH, '//*[@id="anony-nav"]/div[3]/form/span[2]/input')
    # do_search.click()
    # 选择搜索结果的第一个
    try:
        select = web.find_element(By.XPATH, '//div[@class="title"]//a')
    except exceptions.NoSuchElementException:
        web.quit()
        return
    select.click()
    time.sleep(1)
    windows = web.window_handles
    web.switch_to.window(windows[-1])
    time.sleep(1)

    js = "window.scrollTo(0, document.body.scrollHeight)"
    web.execute_script(js)

    # 找到更多评论链接并点击
    # more_comments = web.find_element(By.XPATH, '//*[@id="reviews-wrapper"]/p/a')
    # more_comments.click()

    # 点击查看短评
    try:
        more_comments = web.find_element(By.XPATH, '//div[@class="mod-hd"]/h2//a')
    except exceptions.NoSuchElementException:
        web.quit()
        return
    more_comments.click()
    time.sleep(2)
    reading_comments_url = web.find_element(By.XPATH, '//ul[@class="fleft CommentTabs"]/li[2]/a').get_attribute("href")
    new_comments_url = web.find_element(By.XPATH, '//div[@class="fleft Comments-sortby"]/a[1]').get_attribute("href")
    # print(new_comments_url)
    scrap_one_kind(web, workId, comments)

    web.get(new_comments_url)
    scrap_one_kind(web, workId, comments)

    web.get(reading_comments_url)
    scrap_one_kind(web, workId, comments)

    web.quit()
    if not comments:
        return
    # data = np.array(comments)
    # df = pd.DataFrame(data, columns=['content', 'translated', 'language', 'likes', 'workId',
    #                                  'sentiment', 'country', 'platform', 'postTime'])
    # df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, sep="|", encoding='utf-8')
    return True


def scrap_one_kind(web, workId, comments):
    curr_page = 1
    plan_page = 15
    while curr_page <= plan_page:
        time.sleep(1)
        js = "window.scrollTo(0, document.body.scrollHeight)"
        web.execute_script(js)
        time.sleep(2)
        try:
            comment_wrapper_list = web.find_elements(By.XPATH, '//*[contains(@class, "comment-item")]')
        except exceptions.NoSuchElementException:
            print("没有评论列表")
            continue
        print(comment_wrapper_list)
        for comment_wrapper in comment_wrapper_list:
            try:
                comment = comment_wrapper.find_element(By.XPATH, './/p[contains(@class, "comment-content")]').text
            except exceptions.NoSuchElementException:
                print("找不到评论")
                continue
            comment = text_clean(comment)
            if len(comment.strip()) == 0:
                print("评论内容为空")
                continue
            try:
                post_time = comment_wrapper.find_element(By.XPATH, './/*[contains(@class,"comment-time")]').text
            except exceptions.NoSuchElementException:
                print("找不到时间")
                post_time = '2021-03-02'
            post_time = parse_date_format(post_time)
            try:
                likes = comment_wrapper.find_element(By.XPATH, './/span[contains(@class,"vote-count")]').text.strip()
                if not likes:
                    likes = str(random.randint(0, 5))
            except exceptions.NoSuchElementException:
                print("没有点赞数")
                likes = str(random.randint(0, 5))
            translated = fan_to_jian(comment)
            sentiment = analyze_polarity(translated)
            country = optional_country[random.randint(0, 15)]
            dup = detect_duplicated_comment(workId, country, platform, post_time, comment)
            if dup:
                continue
            success = insert_comment(comment, translated, "汉语", likes, workId, sentiment, country, platform, post_time)
            if not success:
                continue
            comments.append([comment, translated, "汉语", likes, workId, sentiment, country, platform, post_time])

        # 进入下一个评论页
        time.sleep(3)
        try:
            next_page = web.find_element(By.XPATH, '//a[@data-page="next"]')
        except exceptions.NoSuchElementException:
            print("没有下一页按钮")
            break
        next_page.click()
        curr_page = curr_page + 1
    time.sleep(2)


def check_login(web):
    files = os.listdir(base_path + "/profile")
    if "cookies-douban.json" not in files:
        login(web)
    else:
        with open(base_path + "/profile/cookies-douban.json", "r") as f:
            cookies = json.loads(f.read())
        for cookie in cookies:
            if 'expiry' in cookie:
                del cookie['expiry']
                # print(cookie)
            web.add_cookie(cookie)
        time.sleep(1)
        web.refresh()
        time.sleep(3)
    try:
        web.find_element(By.XPATH, '//a[@class="nav-login"]')
        login(web)
    except exceptions.NoSuchElementException:
        return True


def login(web):
    login_nav = web.find_element(By.XPATH, '//a[@class="nav-login"]')
    login_nav.click()
    login_type_btn = web.find_element(By.XPATH, '//ul[@class="tab-start"]/li[2]')
    login_type_btn.click()
    time.sleep(2)
    account_input = web.find_element(By.XPATH, '//input[@class="account-form-input"]')
    passwd_input = web.find_element(By.XPATH, '//input[@class="account-form-input password"]')
    login_btn = web.find_element(By.XPATH, '//a[@class="btn btn-account "]')
    account_input.send_keys('15073548315')
    passwd_input.send_keys('Huang1343111')
    time.sleep(1)
    login_btn.click()
    time.sleep(5)
    cookies = web.get_cookies()
    with open(base_path + '/profile/cookies-douban.json', 'w') as f:
        f.write(json.dumps(cookies))
    time.sleep(1)
    web.get(base_url)
    time.sleep(2)


def scrap_book(keyword, workId):
    scrap_reviews(keyword, workId, 1001)


def scrap_movie(keyword, workId):
    scrap_reviews(keyword, workId, 1002)


if __name__ == "__main__":
    # scrap_movie("青春之歌", 183)
    scrap_book("青春之歌", 184)
