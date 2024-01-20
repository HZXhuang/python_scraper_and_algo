from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import time
import numpy as np
import pandas as pd
from scraper import base_path, get_chrome_options
from scraper.my_utils import identify_lang_to_country, text_clean, \
    parse_date_format, analyze_polarity, fan_to_jian, identify_lang
from scraper.my_translater import youdao_translate
from sql_dao.sql_utils import insert_comment, detect_duplicated_comment

platform = "IMDb"


# 监听某个元素的出现
def get_element_by_xpath(driver, xpath_pattern):
    return WebDriverWait(driver, 20, 1)\
        .until(EC.presence_of_element_located((By.XPATH, xpath_pattern)))


def scrap_reviews(keyword, workId):
    comments = []
    base_url = "https://www.imdb.com"
    driver = webdriver.Chrome(options=get_chrome_options())
    driver.get("https://www.imdb.com/find/?s=tt&q={}&ref_=nv_sr_sm".format(keyword))
    time.sleep(5)
    title_list = driver.find_elements(By.XPATH, '//section[@data-testid="find-results-section-title"]/div[2]/ul/li')
    search_urls = []  # 具体的电影详情链接列表
    for title in title_list:
        search_urls.append(title.find_element(By.XPATH, './/a').get_attribute("href"))
    if len(search_urls) >= 2:
        search_limit = 2
    else:
        search_limit = len(search_urls)
    for i in range(0, len(search_urls)):
        if i + 1 > search_limit:
            break
        search_url = search_urls[i]
        driver.get(search_url)
        time.sleep(1)
        try:
            user_reviews_btn = get_element_by_xpath(driver, '//div[@data-testid="reviews-header"]/div/a')
        except exceptions.TimeoutException as e:
            # print(e)
            print("没有评论")
            continue
        driver.execute_script("arguments[0].click();", user_reviews_btn)  # 点击查看用户评论按钮
        time.sleep(5)
        for j in range(13):
            try:
                load_more_btn = driver.find_element(By.XPATH, '//button[@id="load-more-trigger"]')
                if not load_more_btn.is_displayed():
                    print("加载更多按钮不可见")
                    break
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight - 1000)")
                time.sleep(2)
                driver.execute_script("arguments[0].click();", load_more_btn)
                print("加载更多")
                time.sleep(3)
            except exceptions.NoSuchElementException as e:
                print("找不到加载按钮")
                # print(e)
                break
        comment_wrapper_list = driver.find_elements(By.XPATH, '//div[@data-review-id]')
        for comment_wrapper in comment_wrapper_list:
            try:
                comment = comment_wrapper.find_element(By.XPATH, './/a[@class="title"]').text.replace("\n", "")
            except exceptions.NoSuchElementException:
                print("找不到评论")
                continue
            if len(comment.strip()) == 0:
                print("评论内容为空")
                continue
            try:
                post_time = comment_wrapper.find_element(By.XPATH, './/span[@class="review-date"]').text
            except exceptions.NoSuchElementException:
                print("没有日期")
                post_time = "2023-03-02"
            try:
                likes = comment_wrapper.find_element(By.XPATH, './/div[@class="actions text-muted"]') \
                    .text.strip()
            except exceptions.NoSuchElementException:
                print("没有点赞")
                likes = str(random.randint(0, 5))
            comment = text_clean(comment)
            country = identify_lang_to_country(comment)
            lang = identify_lang(comment)
            if country != "中国":
                translated = youdao_translate(comment)
                # translated = comment
                time.sleep(0.5)
            else:
                translated = comment
            translated = fan_to_jian(translated)
            space_idx = likes.find(" ")
            likes = likes[:space_idx]
            post_time = parse_date_format(post_time)
            sentiment = analyze_polarity(translated)
            dup = detect_duplicated_comment(workId, country, platform, post_time, comment)
            if dup:
                continue
            success = insert_comment(comment, translated, lang, likes, workId, sentiment, country, platform, post_time)
            if not success:
                continue
            comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])

        time.sleep(2)
    driver.quit()
    if not comments:
        return
    # data = np.array(comments)
    # df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
    #                                  'sentiment', 'country', 'platform', 'postTime'])
    # df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, sep="|", encoding='utf-8')
    return True


if __name__ == "__main__":
    scrap_reviews("水浒传", 17)
