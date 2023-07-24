import random

from selenium import webdriver
import time
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import numpy as np
from scraper import base_path, get_chrome_options
from scraper.my_utils import text_clean, parse_date_format, analyze_polarity, identify_lang_to_country
from scraper.my_translater import youdao_translate
from sql_dao.sql_utils import insert_comment

platform = "GoodReads"


def scrap_reviews(keyword, workId):
    comments = []
    driver = webdriver.Chrome(options=get_chrome_options(True))
    driver.get("https://www.goodreads.com/search?utf8=%E2%9C%93&query={}".format(keyword))
    time.sleep(4)
    # book_title = driver.find_element_by_xpath('//a[@class="bookTitle"]')

    # 监听某个元素的出现
    def get_element_by_xpath(driver, xpath_pattern):
        return WebDriverWait(driver, 20, 1)\
            .until(EC.presence_of_element_located((By.XPATH, xpath_pattern)))

    book_title = get_element_by_xpath(driver, '//a[@class="bookTitle"]')
    book_title.click()
    time.sleep(10)
    try:
        # close_btn = driver.find_element_by_xpath('//button[@aria-label="Close"]')
        close_btn = get_element_by_xpath(driver, '//button[@aria-label="Close"]')
        close_btn.click()  # 关闭弹出来的窗口
        time.sleep(2)
    except exceptions.TimeoutException as e:
        print(e)
    show_more_btn1 = driver.find_element(By.XPATH, '//a[@aria-label="Tap to show more reviews and ratings"]')
    # 使用 ActionChains 模拟鼠标操作
    # actions = ActionChains(driver)
    # actions.move_to_element(show_more_btn1).click().perform()   # 点击获取更多评论
    # 使用 JavaScript 执行单击事件
    driver.execute_script("arguments[0].click();", show_more_btn1)  # 用 JavaScript 执行单击事件
    time.sleep(15)
    for i in range(9):
        try:
            show_more_btn2 = driver.find_elements(
                By.XPATH,
                '//button[@class="Button Button--secondary Button--small"]'
            )
            if len(show_more_btn2) < 2:
                break
            show_more_btn2 = show_more_btn2[1]
        except exceptions.NoSuchElementException as e:
            print(e)
            break
        print(show_more_btn2.text)
        driver.execute_script("arguments[0].click();", show_more_btn2)
        time.sleep(8)
    comment_wrappers = driver.find_elements(By.XPATH, '//section[@class="ReviewCard__content"]')
    for comment_wrapper in comment_wrappers:
        try:
            comment = comment_wrapper.find_element(By.XPATH, './/div[@data-testid="contentContainer"]')\
                .text.replace("\n", "")
        except exceptions.NoSuchElementException as e:
            # print(e)
            continue
        if comment.strip() == "":
            continue
        try:
            post_time = comment_wrapper.find_element(By.XPATH, './/span[@class="Text Text__body3"]').text
        except exceptions.NoSuchElementException as e:
            print(e)
            post_time = "2023-03-02"
        try:
            likes = comment_wrapper.find_element(By.XPATH, './/div[@data-testid="stats"]/div[1]')\
                .text.replace("likes", "").replace(",", "").strip()
        except exceptions.NoSuchElementException as e:
            # print(e)
            likes = str(random.randint(0, 5))
        comment = text_clean(comment)  # 清洗
        country = identify_lang_to_country(comment)
        if country != "中国":  # 将不是中文的评论翻译成中文
            translated = youdao_translate(comment)
            # translated = comment
            time.sleep(0.5)
        else:
            translated = comment
        post_time = parse_date_format(post_time)  # 解析日期
        sentiment = analyze_polarity(translated)  # 分析评论的情感极性
        comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])
        insert_comment(comment, translated, likes, workId, sentiment, country, platform, post_time)
    if not comments:
        return
    data = np.array(comments)
    df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
                                     'sentiment', 'country', 'platform', 'postTime'])
    df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, encoding='utf-8')
    return True


if __name__ == "__main__":
    scrap_reviews("Journey to the West Wu Cheng'en", 1)
