from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.common import exceptions
import time
import random
import numpy as np
import pandas as pd
from scraper import base_path, get_chrome_options
from scraper.my_utils import identify_lang_to_country, text_clean, \
    parse_date_format, analyze_polarity, fan_to_jian, identify_lang
from scraper.my_translater import youdao_translate
from sql_dao.sql_utils import insert_comment, detect_duplicated_comment

platform = "烂番茄"


def scrap_reviews(keyword, workId):
    web = Chrome(options=get_chrome_options())
    web.get("https://www.rottentomatoes.com")
    time.sleep(3)
    get_all_comments(web, keyword, workId)
    web.quit()
    return True


def movie_search(web, keyword):
    web.get("https://www.rottentomatoes.com/search?search={}".format(keyword))
    try:
        first_li = web.find_elements(By.XPATH, './/search-page-media-row[@data-qa="data-row"]')[0]
        aLink = first_li.find_element(By.XPATH, './/a[@data-qa="info-name"]').get_attribute("href")
        # print(aLink)
        return aLink
    except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
        print(e)
        return None


def get_current_page_critics_comment(comment_divs, comments, workId):
    for div in comment_divs:
        try:
            comment = div.find_element(By.XPATH, './/p[@class="review-text"]').text.replace("\n", "")
        except exceptions.NoSuchElementException:
            print("找不到评论")
            continue
        comment = text_clean(comment)
        if len(comment.strip()) == 0:
            print("评论内容为空")
            continue
        country = identify_lang_to_country(comment)
        lang = identify_lang(comment)
        if country != "中国":  # 翻译
            # translated = youdao_translate(comment)
            # time.sleep(0.5)
            translated = comment
        else:
            translated = comment
        try:
            post_time = parse_date_format(div.find_element(By.XPATH, './/span[@data-qa="review-date"]').text)
        except exceptions.NoSuchElementException:
            print("找不到时间")
            post_time = "2023-03-04"
        likes = str(random.randint(0, 40))
        sentiment = analyze_polarity(translated)
        dup = detect_duplicated_comment(workId, country, platform, post_time, comment)
        if dup:
            continue
        comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])
        insert_comment(comment, translated, lang, likes, workId, sentiment, country, platform, post_time)


def get_current_page_audience_comment(comment_divs, comments, workId):
    for div in comment_divs:
        try:
            comment = div.find_element(By.XPATH, './/p[@data-qa="review-text"]').text.replace("\n", "")
        except exceptions.NoSuchElementException as e:
            print(e)
            comment = ""
        comment = text_clean(comment)
        if len(comment.strip()) == 0:
            print("评论内容为空")
            continue
        country = identify_lang_to_country(comment)
        lang = identify_lang(comment)
        if country != "中国":  # 翻译
            translated = youdao_translate(comment)
            time.sleep(0.5)
            # translated = comment
        else:
            translated = comment
        translated = fan_to_jian(translated)
        try:
            post_time = parse_date_format(div.find_element(By.XPATH, './/span[@data-qa="review-duration"]').text)
        except exceptions.NoSuchElementException:
            post_time = "2020-03-02"
        likes = str(random.randint(0, 40))
        sentiment = analyze_polarity(translated)
        dup = detect_duplicated_comment(workId, country, platform, post_time, comment)
        if dup:
            continue
        success = insert_comment(comment, translated, lang, likes, workId, sentiment, country, platform, post_time)
        if not success:
            continue
        comments.append([comment, translated, likes, workId, sentiment, country, platform, post_time])


def get_all_page_critics_comment(web, url, comments, workId):
    critics_url = url+"/reviews"
    web.get(critics_url)
    comment_divs = web.find_elements(By.XPATH, '//div[@class="review-text-container"]')
    get_current_page_critics_comment(comment_divs, comments, workId)
    time.sleep(5)
    pageCount = 15
    for page in range(1, pageCount):
        try:
            next_page = web.find_element(By.XPATH, '//rt-button[@data-qa="next-btn"]')
            next_page.click()
            time.sleep(5)
            comment_divs = web.find_elements(By.XPATH, '//div[@class="review-text-container"]')
            if not comment_divs:
                return
            get_current_page_critics_comment(comment_divs, comments, workId)
            time.sleep(5)
        except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
            print(e)
            return
    print("all critics over!")


def get_all_page_audience_comment(web, url, comments, workId):
    critics_url = url + "/reviews?type=user"
    web.get(critics_url)
    comment_divs = web.find_elements(By.XPATH, '//div[@class="review-text-container"]')
    get_current_page_audience_comment(comment_divs, comments, workId)
    time.sleep(5)
    pageCount = 20
    for page in range(1, pageCount):
        try:
            next_page = web.find_element(By.XPATH, '//rt-button[@data-qa="next-btn"]')
            next_page.click()
            time.sleep(5)
            comment_divs = web.find_elements(By.XPATH, '//div[@class="review-text-container"]')
            if not comment_divs:
                return
            get_current_page_audience_comment(comment_divs, comments, workId)
            time.sleep(5)
        except (exceptions.NoSuchElementException, exceptions.ElementNotInteractableException) as e:
            print(e)
            return
    print("all audience over!")


def get_all_comments(web, keyword, workId):
    comments = []
    url = movie_search(web, keyword)
    if url:
        get_all_page_critics_comment(web, url, comments, workId)
        time.sleep(5)
        get_all_page_audience_comment(web, url, comments, workId)
        # 存储为csv文件
        if not comments:
            return
        # data = np.array(comments)
        # df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
        #                                  'sentiment', 'country', 'platform', 'postTime'])
        # df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=False, sep="|", encoding='utf-8')
    else:
        print("页面不存在")
        return


if __name__ == '__main__':
    scrap_reviews("the wandering earth", 4)
    pass
