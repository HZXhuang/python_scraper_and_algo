import langid
import random
from scraper import base_path
from scraper import code_country_map
import os
import re
from snownlp import SnowNLP
import pandas as pd


# 识别句子的语言，并返回所属国家
def identify_lang_to_country(sentence):
    la_id = langid.classify(sentence)
    print(la_id)
    try:
        country = code_country_map[la_id[0]]
        # print(type(country))
        if type(country) == list:
            idx = random.randint(0, len(country) - 1)
            return country[idx]
        else:
            return country
    except KeyError as e:
        print(e)
        return "未知国家"


def check_exists_and_make_dir(dir_name):
    dir_path = base_path + "/{}".format(dir_name)
    if dir_name not in os.listdir(base_path):
        os.mkdir(dir_path)


# 对文本进行清洗，去除html标签，将一些特殊字符进行转换
def text_clean(text):
    pattern = re.compile(r'<[^>]+>', re.S)
    result = pattern.sub("", text).replace("&quot;", "").replace("&#39;", "'").replace("\"", "")
    # print(result)
    return result


# 分析文本所包含的情感极性，积极或消极
def analyze_polarity(text):
    res = SnowNLP(text)
    # print(res.sentiments)
    if res.sentiments < 0.45:
        return "消极"
    elif res.sentiments < 0.55:
        return "中立"
    else:
        return "积极"


# 解析字符串时间，返回标准格式的日期
def parse_date_format(time_text):
    if "年" in time_text:
        return time_text.replace("年", "-").replace("月", "-").replace("日", "")
    else:
        res = pd.to_datetime(time_text)
        return str(res.date())


if __name__ == "__main__":
    print(identify_lang_to_country("barbie is way better than the wandering earth芭比爆杀流浪地球"))
    # res = text_clean('<a href="https://www.youtube.com/watch?v=i-XvSRyOUbc&amp;t=2m35s">2:35</a> : 他说&quot;什么？I&#39;"  \'"""我听说“史密斯不的铁的吗&quot;')
    # print(res)
    # print(analyze_polarity("An incredibly bad film with poor CGI and no character development"))
    # print(parse_date_format("2023-07-18T04:59:05.000Z"))
    pass