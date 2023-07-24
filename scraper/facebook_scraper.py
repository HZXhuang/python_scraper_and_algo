import os
import random
import re
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from scraper.my_utils import identify_lang_to_country, analyze_polarity, \
    text_clean, parse_relative_date, parse_num
from scraper.my_translater import youdao_translate
from scraper import base_path, get_chrome_options
from sql_dao.sql_utils import insert_comment


platform = "Facebook"


def get_element_by_xpath(driver, xpath_pattern):
    return WebDriverWait(driver, 20, 1)\
        .until(EC.presence_of_element_located((By.XPATH, xpath_pattern)))


def create_webdriver_instance():
    br = webdriver.Chrome(options=get_chrome_options(True))
    br.get("https://facebook.com")
    # 从文件中读取cookies
    with open(base_path + "/profile/cookies-facebook.json", "r") as f:
        cookies = json.loads(f.read())
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
            # print(cookie)
        br.add_cookie(cookie)
    br.refresh()
    time.sleep(2)
    return br


def extract_video_comments(driver, url, comments, workId, max_video_comment_num):
    driver.get(url)
    time.sleep(3)
    # try:
    #     right_btns = driver.find_elements(By.XPATH, '//div[@class="xjkvuk6 x1y1aw1k"]')
    # except exceptions.NoSuchElementException:
    #     print("找不到按钮")
    #     return
    # if len(right_btns) != 2:
    #     print("没有评论按钮")
    #     return
    # comment_btn = right_btns[1]  # 评论按钮
    # # print(comment_btn.text)
    # driver.execute_script("arguments[0].click();", comment_btn)
    time.sleep(4)
    try:
        show_more_btn = driver.find_element(By.XPATH, '//div[@class="x78zum5 x13a6bvl xdj266r '
                                                      'xktsk01 xat24cr x1d52u69"]//span[@class="x78zum5 '
                                                      'x1w0mnb xeuugli"]')
        driver.execute_script("arguments[0].click();", show_more_btn)
        time.sleep(8)
    except exceptions.NoSuchElementException:
        print("没有查看更多评论按钮")
    try:
        comment_wrapper_list = driver.find_elements(
            By.XPATH,
            '//div[@class="x1n2onr6 x1iorvi4 x4uap5 x18d9i69 x1swvt13 x78zum5 x1q0g3np x1a2a7pz"]'
        )
    except exceptions.NoSuchElementException:
        print("没有评论")
        return
    # 遍历每一个评论块
    for i in range(len(comment_wrapper_list)):
        if i >= max_video_comment_num:
            break
        comment_wrapper = comment_wrapper_list[i]
        try:
            comment = comment_wrapper.find_element(
                By.XPATH,
                './/div[@class="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs"]'
            ).text.replace("\n", "")
        except exceptions.NoSuchElementException:
            print("找不到这条评论")
            continue
        comment = text_clean(comment)
        if len(comment.strip()) == 0:
            continue
        # 提取点赞数
        try:
            likes = comment_wrapper.find_element(
                By.XPATH,
                './/span[@class="xi81zsa x1nxh6w3 x1fcty0u x1sibtaa xexx8yu xg83lxy x18d9i69 x1h0ha7o xuxw1ft"]'
            ).text.strip()
            if not likes:
                likes = str(random.randint(0, 5))
        except exceptions.NoSuchElementException:
            print("没有点赞数")
            likes = str(random.randint(0, 5))
        # 提取日期
        try:
            raw_date = comment_wrapper.find_elements(
                By.XPATH,
                './/li[@class="x1rg5ohu x1emribx x1i64zmx"]'
            )[2].text.strip()
            post_time = str(parse_relative_date(raw_date))
        except (exceptions.NoSuchElementException, IndexError):
            print("找不到时间")
            post_time = "2023-03-04"
        country = identify_lang_to_country(comment)
        if country != "中国":
            translated = youdao_translate(comment)
            time.sleep(0.5)
            # translated = comment
        else:
            translated = comment
        sentiment = analyze_polarity(translated)
        comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])
        insert_comment(comment, translated, likes, workId, sentiment, country, platform, post_time)
    pass


def login_facebook():
    br = webdriver.Chrome(options=get_chrome_options(True))
    br.get("https://facebook.com/login")
    # 填写手机号或邮箱
    time.sleep(2)
    user_name = get_element_by_xpath(br, '//input[@id="email"]')
    user_name.send_keys('hzx1966752024@163.com')

    # 填写密码
    password_input = get_element_by_xpath(br, '//input[@id="pass"]')
    password_input.send_keys('@h1343111')
    time.sleep(2)
    # 登陆
    get_element_by_xpath(br, '//button[@id="loginbutton"]').click()
    time.sleep(8)
    cookies = br.get_cookies()
    # print(cookies)
    with open(base_path + '/profile/cookies-facebook.json', 'w') as f:
        f.write(json.dumps(cookies))
    time.sleep(2)
    br.quit()


def main(keyword, workId):
    max_video_num = 6
    max_video_comment_num = 50
    comments = []
    br = create_webdriver_instance()
    time.sleep(1)
    br.get("https://www.facebook.com/search/videos?q={}".format(keyword))
    time.sleep(3)
    for i in range(2):
        br.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)
    time.sleep(2)
    video_wrapper_list = br.find_elements(By.XPATH,
                                          '//div[@role="article"]'
                                          )
    video_url_list = []
    for video_wrapper in video_wrapper_list:
        video_url = video_wrapper.find_element(By.XPATH, './/a').get_attribute("href")
        raw_watch_num = video_wrapper.find_element(
            By.XPATH, './/span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1nxh6w3 x1sibtaa xo1l8bm xi81zsa"]'
        ).text.strip()
        print(raw_watch_num)
        print(video_url)
        try:
            raw_watch_num = re.findall(r'日 ·(.*?)次播放', raw_watch_num, re.S)[0]
        except IndexError:
            raw_watch_num = "0"
        watch_num = parse_num(raw_watch_num)
        video_url_list.append((watch_num, video_url))
    # video_list = br.find_elements(By.XPATH, '//div[@role="article"]//a')
    # 提取视频链接
    # for video in video_list:
    #     video_url_list.append(video.get_attribute("href"))
    # 截取过多的视频链接列表
    video_url_list.sort(reverse=True)
    if len(video_url_list) > max_video_num:
        video_url_list = video_url_list[:max_video_num-1]
    # 遍历视频链列表
    for video_url in video_url_list:
        extract_video_comments(br, video_url[1], comments, workId, max_video_comment_num)
        time.sleep(1)
    # print(video_url_list)
    time.sleep(2)
    if not comments:
        return
    data = np.array(comments)
    df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
                                     'sentiment', 'country', 'platform', 'postTime'])
    df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, encoding='utf-8')
    return True


def scrap_reviews(keyword, workId):
    files = os.listdir(base_path + "/profile")
    if "cookies-facebook.json" not in files:
        login_facebook()
    return main(keyword, workId)


if __name__ == "__main__":
    scrap_reviews("李子柒短视频", 5)
