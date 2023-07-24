import langid
import random
from scraper import base_path, max_comment_len
from scraper import code_country_map
import os
import re
from snownlp import SnowNLP
import pandas as pd
from pypinyin import lazy_pinyin
from datetime import datetime


# 识别句子的语言，并返回所属国家
def identify_lang_to_country(sentence):
    la_id = langid.classify(sentence)
    # print(la_id)
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
    if len(result) >= max_comment_len:
        result = result[:max_comment_len - 1]
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


# 通过距离当前时间长度计算日期
def parse_relative_date(time_text: str):
    if "年" in time_text:
        formatted = datetime.now() - pd.Timedelta(days=int(time_text.replace("年", ""))*365)
    elif "月" in time_text:
        formatted = datetime.now() - pd.Timedelta(days=int(time_text.replace("月", ""))*30)
    elif "周" in time_text:
        formatted = datetime.now() - pd.Timedelta(weeks=int(time_text.replace("周", "")))
    elif "天" in time_text:
        formatted = datetime.now() - pd.Timedelta(days=int(time_text.replace("天", "")))
    elif "小时" in time_text:
        formatted = datetime.now() - pd.Timedelta(hours=int(time_text.replace("小时", "")))
    elif "分钟" in time_text:
        formatted = datetime.now() - pd.Timedelta(minutes=int(time_text.replace("分钟", "")))
    else:
        formatted = datetime.now()
    return formatted.date()


# 解析数字 播放次数
def parse_num(text: str):
    if "万" in text:
        return float(text.replace("万", "").replace(" ", "").replace(",", ""))*10000
    else:
        return float(text.replace(",", "").replace(" ", ""))


# 将中文转换成拼音
def chinese_to_pinyin(sentence):
    res = lazy_pinyin(sentence)
    return " ".join(res)


if __name__ == "__main__":
    # print(identify_lang_to_country("barbie is way better than the wandering earth芭比爆杀流浪地球"))
    # res = text_clean('<a href="https://www.youtube.com/watch?v=i-XvSRyOUbc&amp;t=2m35s">2:35</a> : 他说&quot;什么？I&#39;"  \'"""我听说“史密斯不的铁的吗&quot;')
    # print(res)
    # text = "Who am I to write a review of a collection of 600 year old Chinese fairytales? This edition, with notes about the translation and a great introduction, and with its updated language, is accessible, fun, and despite what Goodreads thinks, I read this over the course of a week or so, in enjoyable chunks, probably more like what was intended. I recommend this to anyone who'd like a grounding in Chinese myth or culture that they don't already have."[:150]
    # print(text)
    # print(analyze_polarity("我凭什么给一本600年的中国童话写评论?这个版本，有关于翻译的注释和一个很好的介绍"))
    # print(parse_date_format("2023-07-18T04:59:05.000Z"))
    # print(chinese_to_pinyin("流浪地球"))
    print(parse_relative_date("4天"))
    pass