from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import re
import time
import random
import numpy as np
import pandas as pd
from scraper import base_path, get_chrome_options
from scraper.my_utils import identify_lang_to_country, text_clean, \
    parse_date_format, analyze_polarity, fan_to_jian
from scraper.my_translater import youdao_translate
from sql_dao.sql_utils import insert_comment

platform = "Amazon"
country_rex = '在(.*?)发布'
country_rex2 = '在(.*?)审核'
time_rex = r'\d+年\d+月\d+日'


def scrap_reviews(keyword, workId):
    curr_page = 1
    plan_page = 20
    comments = []
    web = webdriver.Chrome(options=get_chrome_options(False))  # 获取浏览器驱动
    search = keyword.replace(" ", "+")
    # 访问亚马逊搜索页面
    web.get(
        "https://www.amazon.com/s?k={}&__mk_zh_CN=亚马逊平台&crid=30S6TSEQ3D6Z7&sprefix={}&ref=nb_sb_noss_1"
            .format(search, search)
    )
    time.sleep(4)
    search_result = web.find_element(
        By.XPATH,
        '//a[@class="a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal"]'
    )
    search_result.click()
    # journey to the west
    time.sleep(3)
    js = "window.scrollTo(0, document.body.scrollHeight)"
    web.execute_script(js)
    time.sleep(0.5)
    try:
        see_more_btn = web.find_element(By.XPATH, '//a[@data-hook="see-all-reviews-link-foot"]')
        see_more_btn.click()  # 点击查看更多评论按钮
    except exceptions.NoSuchElementException:
        extract_comments(web, comments, workId)
        print("没有查看更多评论按钮")
        return
    time.sleep(0.5)
    while curr_page <= plan_page:
        extract_comments(web, comments, workId)
        # 跳转下一页
        curr_page = curr_page + 1
        try:
            next_page = web.find_element(By.XPATH, '//*[@id="cm_cr-pagination_bar"]/ul/li[2]/a')
            time.sleep(2)
            next_page.click()
        except exceptions.NoSuchElementException:
            print("没有下一页按钮")
            break
    if not comments:
        return
    data = np.array(comments)
    df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
                                     'sentiment', 'country', 'platform', 'postTime'])
    df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, sep="|", encoding='utf-8')
    return True


def extract_comments(web, comments, workId):
    time.sleep(2)
    js = "window.scrollTo(0, document.body.scrollHeight)"
    web.execute_script(js)
    time.sleep(1)
    # 获取评论的Element
    try:
        comment_wrapper_list = web.find_elements(By.XPATH, '//div[@data-hook="review"]')
    except exceptions.NoSuchElementException:
        print("没有评论")
        return
    for comment_wrapper in comment_wrapper_list:
        try:
            comment = comment_wrapper.find_element(By.XPATH, './/span[@data-hook="review-body"]') \
                .text.replace("\n", "")
        except exceptions.NoSuchElementException:
            print("找不到评论")
            continue
        comment = text_clean(comment)
        if len(comment.strip()) == 0:
            print("评论内容为空")
            continue
        try:
            time_and_country = comment_wrapper.find_element(By.XPATH, './/span[@data-hook="review-date"]').text
        except exceptions.NoSuchElementException:
            time_and_country = "2021年8月28日 在美国审核"
            print("没有找到国家和日期")
        try:
            likes = re.findall(r'\d+', comment_wrapper.find_element(
                By.XPATH,
                './/span[@data-hook="helpful-vote-statement"]').text, re.S)
            if len(likes) >= 1:
                likes = likes[0]
        except exceptions.NoSuchElementException:
            print("没有点赞数")
            likes = str(random.randint(0, 5))
        time1 = re.findall(time_rex, time_and_country, re.S)[0]
        post_time = parse_date_format(time1)
        country = re.findall(country_rex, time_and_country, re.S)
        if len(country) == 0:
            country = re.findall(country_rex2, time_and_country, re.S)
        # 去除国家里面的英文字母
        country = re.sub('[a-zA-Z]', '', country[0])
        lang_country = identify_lang_to_country(comment)
        if lang_country != "中国":
            translated = youdao_translate(comment)
            time.sleep(0.5)
            # translated = comment
        else:
            translated = comment
        translated = fan_to_jian(translated)
        sentiment = analyze_polarity(translated)
        # 把评论的所有信息插入列表中
        success = insert_comment(comment, translated, likes, workId, sentiment, country, platform, post_time)
        if not success:
            continue
        comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])


if __name__ == "__main__":
    scrap_reviews("A Dream of Red Mansions", 8)
