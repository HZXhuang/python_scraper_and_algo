import os.path

import jieba
from jieba.analyse import extract_tags
import re
from collections import Counter
from sql_dao.sql_utils import conn
from scraper.my_utils import analyze_word_polarity
import pandas as pd
import numpy as np
from pymysql.err import ProgrammingError, MySQLError
from tkinter import _flatten

node_num = 25
base_dir = base_path = os.path.dirname(os.path.abspath(__file__))


def load_prefer_word_dict(fpath=base_dir + "/data/preferDict.txt"):
    jieba.load_userdict(fpath)


def add_word(word: str):
    jieba.add_word(word)


# 获取停用词列表
def get_stopwords_list():
    stopwords = [line.strip() for line in
                 open(base_dir + '/data/stopwords_cn.txt', "r", encoding="utf-8").readlines()]
    #  停用词补充
    stopwords.append("~")
    # ///
    return stopwords


# 对句子进行中文分词
def seg_depart(sentence):
    print('正在分词')
    sentence_depart = jieba.cut(sentence.strip())
    # 创建一个停用词列表
    stopwords = get_stopwords_list()
    # 输出结果为 outstr
    outstr = ''
    #     去停用词
    for word in sentence_depart:
        if word not in stopwords:
            if word != '\t' and word != ' ':
                outstr += word
                outstr += " "
    return outstr


def extract_term(sentence):
    tags = jieba.analyse.extract_tags(sentence, topK=100)
    return " ".join(tags)


def count_from_file(file, top_limit=0):
    with open(file, "r", encoding="utf-8") as f:
        content = f.read()
        # 将多个空格替换为一个空格
        content = re.sub(r'\s+', r' ', content)
        content = re.sub(r'\.+', r' ', content)
        # 去停用词
        content = seg_depart(content)

        return count_from_str(content, top_limit=top_limit)


def gather_info(word_counts: list):
    polarities = []
    keywords = []
    frequencies = []
    for item in word_counts:
        keywords.append(item[0])
        frequencies.append(str(item[1]))
        polarities.append(analyze_word_polarity(item[0]))
    return " ".join(polarities), " ".join(keywords), " ".join(frequencies)


def count_from_str(content, top_limit=0):
    if top_limit <= 0:
        top_limit = 50
    #     提取文章的关键词
    tags = jieba.analyse.extract_tags(content, topK=100)

    words = jieba.cut(content)

    counter = Counter()
    for word in words:
        if word in tags:
            counter[word] += 1

    return counter.most_common(top_limit)


# 从数据库中取出评论数据进行分词和词频统计，然后再写入数据库的“词频统计表”
def count_from_db(workId, country, platform, post_time):
    sql = """
        select translated from raw_comment 
        where workId = {} and country = "{}" and platform = "{}"
        and postTime = "{}";
    """.format(workId, country, platform, post_time)
    comments = pd.read_sql(sql=sql, con=conn)
    if len(comments) == 0:
        # print("没有评论")
        return
    comments = comments["translated"].tolist()  # 获取查询到的评论列表
    comments = seg_depart(' '.join(comments))  # 将所有评论合并在一起
    res_tuple = gather_info(count_from_str(comments))
    if len(res_tuple[0]) == 0:
        return
    # print(res_tuple)
    # print(comments)
    cursor = conn.cursor()
    sql_query = """
        select * from word_freq_analy where workId = {} and country = "{}"
        and platform = "{}" and time = "{}";
    """.format(workId, country, platform, post_time)
    sql_delete = """
        delete from word_freq_analy where workId = {} and country = "{}"
        and platform = "{}" and time = "{}";
    """.format(workId, country, platform, post_time)
    cursor.execute(sql_query)
    if len(cursor.fetchall()) > 0:
        cursor.execute(sql_delete)
    sql_insert = """
                insert into word_freq_analy(workId, country, platform,
                time, polarity, keywords, frequency) values({}, "{}", "{}", "{}", "{}", "{}", "{}");
            """.format(workId, country, platform, post_time, res_tuple[0], res_tuple[1], res_tuple[2])
    try:
        cursor.execute(sql_insert)
        conn.commit()  # 提交修改
    except (MySQLError, ProgrammingError):
        print("插入失败，有错误")
    # print(len(cursor.fetchall()))


def count_words_by_workId(workId):
    load_prefer_word_dict()  # 加载自定义词汇表
    sql1 = "select distinct country from raw_comment where workId = %d" % workId
    sql2 = "select distinct platform from raw_comment where workId = %d" % workId
    sql3 = "select distinct postTime from raw_comment where workId = %d" % workId
    # 分别获取workId号作品的评论所属的国家列表、平台列表、发布时间列表
    countries = pd.read_sql(sql1, con=conn)["country"].tolist()
    platforms = pd.read_sql(sql2, con=conn)["platform"].tolist()
    post_times = pd.read_sql(sql3, con=conn)["postTime"].tolist()
    # print(countries)
    # print(platforms)
    # print(post_times)
    for country in countries:
        for platform in platforms:
            for post_time in post_times:
                count_from_db(workId, country, platform, post_time)
    return True


def compute_matrix(df: pd.DataFrame):
    reviews = df["translated"].tolist()
    content = []
    for review in reviews:
        div_words = extract_term(seg_depart(review))  # 提取评论的主题词
        if len(div_words) > 0:
            content.append(div_words)

    # print(content)
    cut_word_list = list(map(lambda x: ''.join(x), content))
    # print(cut_word_list)
    content_str = ' '.join(content).split()  # 提取出所有的词语，得到一个一维列表
    # print(content_str)
    word_fre = pd.Series(_flatten(content_str)).value_counts()  # 统计词频
    high_freq_word_num = min(len(word_fre), 50)  # 共现语义网络中最大的单词数
    # print(word_fre[:high_freq_word_num])
    # word_fre[:high_freq_word_num].to_excel("./流浪地球词频统计表.xlsx")
    keywords = word_fre[:high_freq_word_num].index
    # freq = word_fre[:high_freq_word_num].tolist()
    # freq = list(map(lambda x: str(x), freq))
    # print(word_fre)
    # print(' '.join(keywords))
    # print(' '.join(freq))
    # print(word_fre)
    matrix = np.zeros((len(keywords) + 1) * (len(keywords) + 1)).reshape(len(keywords) + 1, len(keywords) + 1).astype(
        str)
    matrix[0][0] = np.NaN
    matrix[1:, 0] = matrix[0, 1:] = keywords

    cont_list = [cont.split() for cont in cut_word_list]
    for i, w1 in enumerate(word_fre[:high_freq_word_num].index):
        for j, w2 in enumerate(word_fre[:high_freq_word_num].index):
            count = 0
            for cont in cont_list:
                if w1 in cont and w2 in cont:
                    if abs(cont.index(w1) - cont.index(w2)) == 0 or abs(cont.index(w1) - cont.index(w2)) == 1:
                        count += 1
            matrix[i + 1][j + 1] = count
    kwdata = pd.DataFrame(data=matrix)
    return kwdata
    # kwdata.to_csv('关键词共现矩阵.csv', index=False, header=False, encoding='utf-8')


# 生成共现语义网络图的节点和边的信息
def generate_gram_matrix(workId, country, post_time):
    sql_query = """
        select translated from raw_comment
        where workId = {} and country = "{}" and postTime = "{}"
    """.format(workId, country, post_time)
    res_data = pd.read_sql(sql=sql_query, con=conn)
    gram_matrix = compute_matrix(res_data)
    # gram_matrix.index = gram_matrix.iloc[:, 0].tolist()
    # print(gram_matrix)
    word_names = gram_matrix[0].tolist()[1:]
    # print(word_names)
    aja_table = []
    for i in range(1, node_num+1):
        for j in range(i + 1, node_num):
            val = int(gram_matrix.iloc[i, j])
            if val > 0:
                aja_table.append([word_names[i], word_names[j], val])
    # 返回结点列表，即关键词 和 邻接表
    return {"nodes": word_names, "edges": aja_table}


if __name__ == "__main__":
    # load_prefer_word_dict()
    # res = seg_depart("纵观中国科幻电影，《流浪地球2》无疑是破天荒的存在。不过从两个纬度——电影制作、科幻品位来分析，寻找优秀之余的缺憾，才是批评的价值。电影在这两个范畴内都存在着诸多缺失。 （1）制作 面子十足，里子不足。 面子是声光画和娱乐性，里子是剧情台本和剪辑。 娱乐性此处指...  ")
    # print(res)
    # print(extract_term(res))
    # print(gather_info(res))
    # count_from_db(4, "中国", "豆瓣", "2023-01-2")
    count_words_by_workId(1)
    # res = generate_gram_matrix(4, "中国", "2023-01-23")
    # print(res)
    pass
