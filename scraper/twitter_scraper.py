import os
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import csv
from scraper.my_utils import identify_lang_to_country, analyze_polarity, text_clean, parse_date_format
from scraper.my_translater import youdao_translate
from scraper import base_path, get_chrome_options
from sql_dao.sql_utils import insert_comment


def get_element_by_xpath(driver, xpath_pattern):
    return WebDriverWait(driver, 20, 1)\
        .until(EC.presence_of_element_located((By.XPATH, xpath_pattern)))


def create_webdriver_instance():
    br = webdriver.Chrome(chrome_options=get_chrome_options(True))
    br.get("https://twitter.com")
    # 从文件中读取cookies
    with open(base_path + "/profile/cookies-twitter.json", "r") as f:
        cookies = json.loads(f.read())
    for cookie in cookies:
        if 'expiry' in cookie:
            del cookie['expiry']
            # print(cookie)
        br.add_cookie(cookie)
    return br


def twitter_search(br, keyword, search_type):
    # br.maximize_window()
    br.get("https://twitter.com/search?q={}&src=typed_query&f={}".format(keyword, search_type))
    time.sleep(5)
    return True


def generate_tweet_id(tweet):
    return ''.join(tweet)


def scroll_down_page(driver, last_position, num_seconds_to_load=1.5, scroll_attempt=0, max_attempts=5):
    """页面滚动  因为页面元素会动态刷新，所以每次滚动合适的长度"""
    end_of_scroll_region = False
    driver.execute_script("window.scrollBy(0, 1500);")
    time.sleep(num_seconds_to_load)
    curr_position = driver.execute_script("return window.pageYOffset;")
    if curr_position == last_position:
        if scroll_attempt < max_attempts:
            end_of_scroll_region = True
        else:
            scroll_down_page(last_position, curr_position, scroll_attempt + 1)
    last_position = curr_position
    return last_position, end_of_scroll_region


def save_tweet_data_to_csv(records, filepath, workId, mode='a+'):
    header = ['content', 'translated', 'likes', 'workId', 'sentiment', 'country', 'platform', 'postTime']
    with open(filepath, mode=mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if mode == 'w':
            writer.writerow(header)
        if records:
            row = list(records)
            country = identify_lang_to_country(row[0])
            if country != "中国":
                row.insert(1, youdao_translate(row[0]))
            else:
                row.insert(1, str(row[0]))
            row.insert(3, workId)
            row.insert(4, analyze_polarity(row[1]))
            row.insert(5, country)
            row.insert(6, "Twitter")
            row.append("Twitter")
            insert_comment(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
            writer.writerow(row)


def collect_all_tweets_from_current_view(driver, limit=25):
    """The page is continously loaded, so as you scroll down the number of tweets returned by this function will
     continue to grow. To limit the risk of 're-processing' the same tweet over and over again, you can set the
     `lookback_limit` to only process the last `x` number of tweets extracted from the page in each iteration.
     You may need to play around with this number to get something that works for you. I've set the default
     based on my computer settings and internet speed, etc..."""
    page_cards = driver.find_elements_by_xpath('//article[@data-testid="tweet"]')
    if len(page_cards) <= limit:
        return page_cards
    else:
        return page_cards[-limit:]


def extract_data_from_current_tweet_card(card):
    try:
        """
        If there is no post date here, there it is usually sponsored content, or some
        other form of content where post dates do not apply. You can set a default value
        for the postdate on Exception if you which to keep this record. By default I am
        excluding these.
        """
        post_time = card.find_element_by_xpath('.//time').get_attribute('datetime')
    except exceptions.NoSuchElementException as e:
        print(e)
        post_time = "2023-03-01T11:44:32.000Z"
    try:
        _comment = card.find_element_by_xpath('.//div[@data-testid=\"tweetText\"]').text.replace("\n", "")
    except exceptions.NoSuchElementException as e:
        print(e)
        _comment = ""
    try:
        likes = card.find_element_by_xpath('.//div[@data-testid="like"]').text.replace(",", "").strip()
    except exceptions.NoSuchElementException as e:
        print(e)
        likes = "0"
    if likes == "":
        likes = "0"

    tweet = (text_clean(_comment), likes, parse_date_format(post_time))
    return tweet


def login_twitter():
    # 需要代理
    br = webdriver.Chrome(options=get_chrome_options(True))
    br.get("https://twitter.com/i/flow/login")
    # 填写手机号
    # time.sleep(5)
    user_name = get_element_by_xpath(br, "//input")
    next_btn = get_element_by_xpath(br, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")
    user_name.send_keys('hzx1966752024@163.com')
    # 点击下一步
    next_btn.click()
    # time.sleep(5)

    # 用户名验证
    verify_username = get_element_by_xpath(br, "//*[@id=\"layers\"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div[2]/label/div/div[2]/div/input")
    next_btn2 = get_element_by_xpath(br, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div/div/div/div')
    verify_username.send_keys("hzx1966752024")
    next_btn2.click()
    # time.sleep(2)

    # 填写密码
    password_input = get_element_by_xpath(br, "//input[@name=\"password\"]")
    password_input.send_keys('1343111Huang')

    # 登陆
    get_element_by_xpath(br, '//*[@id="layers"]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div').click()
    time.sleep(8)
    cookies = br.get_cookies()
    # print(cookies)
    with open(base_path + '/profile/cookies-twitter.json', 'w') as f:
        f.write(json.dumps(cookies))
    time.sleep(2)
    br.quit()


def main(keyword, filepath, tab_name, unique_tweets, max_num, workId):
    last_pos = None
    end_of_page = False
    br = create_webdriver_instance()
    search_page = twitter_search(br, keyword, tab_name)
    if not search_page:
        return
    while not end_of_page:
        if len(unique_tweets) >= max_num:
            return
        cards = collect_all_tweets_from_current_view(br)
        for card in cards:
            try:
                comment = extract_data_from_current_tweet_card(card)
            except exceptions.StaleElementReferenceException as e:
                print(e)
                continue
            if not comment:
                continue
            tweet_id = generate_tweet_id(comment)
            if tweet_id not in unique_tweets:
                unique_tweets.add(tweet_id)
                save_tweet_data_to_csv(comment, filepath, workId)
        last_pos, end_of_page = scroll_down_page(br, last_pos)
    print(unique_tweets)
    print(len(unique_tweets))


def scrap_twitter(keyword, workId):
    files = os.listdir(base_path + "/profile")
    if "cookies-twitter.json" not in files:
        login_twitter()
    max_tweets = 300  # 最多可获取的推文数
    tab_names = ["hot", "image", "video"]
    unique_tweets = set()
    path = base_path + "/out/{}_Twitter.csv".format(keyword)
    save_tweet_data_to_csv(None, path, workId, mode='w')  # 创建一个新的文件
    for tab_name in tab_names:
        main(keyword, path, tab_name, unique_tweets, max_tweets, workId)
    return True


if __name__ == "__main__":
    # login_twitter()
    # print(files)
    scrap_twitter("流浪地球", 2)
