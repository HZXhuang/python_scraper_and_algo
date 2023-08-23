import os.path

import jieba
from jieba.analyse import extract_tags
import re
from collections import Counter
from sql_dao import db_engine, get_db_session
from scraper.my_utils import analyze_word_polarity
import pandas as pd
import numpy as np
from sqlalchemy.exc import ProgrammingError, SQLAlchemyError
from tkinter import _flatten
import gensim
from gensim import corpora
from gensim.models import LdaModel, CoherenceModel
from sqlalchemy import text

import matplotlib.pyplot as plt
import matplotlib

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
    stopwords.append("http")
    stopwords.append("https")
    # ///
    return stopwords


# 对句子进行中文分词
def seg_depart(sentence):
    # print('正在分词')
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


# 计算coherence 主题一致性
def coherence(num_topics, corpus, dictionary, data_set):
    ldamodel = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=30, random_state=1)
    print(ldamodel.print_topics(num_topics=num_topics, num_words=10))
    ldacm = CoherenceModel(model=ldamodel, texts=data_set, dictionary=dictionary, coherence='c_v')
    print(ldacm.get_coherence())
    return ldacm.get_coherence()


def lda_extract_terms(df: pd.DataFrame):
    data_set = []
    for comment in df["translated"].tolist():
        data_set.append(seg_depart(comment).split(" "))
    dictionary = corpora.Dictionary(data_set)
    corpus = [dictionary.doc2bow(text) for text in data_set]
    # x = range(1, 15)
    # # z = [perplexity(i) for i in x]  #如果想用困惑度就选这个
    # y = [coherence(i, corpus, dictionary, data_set) for i in x]
    # plt.plot(x, y)
    # plt.xlabel('主题数目')
    # plt.ylabel('coherence大小')
    # plt.rcParams['font.sans-serif'] = ['SimHei']
    # matplotlib.rcParams['axes.unicode_minus'] = False
    # plt.title('主题-coherence变化情况')
    # plt.show()
    lda = LdaModel(corpus=corpus, id2word=dictionary, num_topics=3, passes=50, random_state=1)
    topic_list = lda.print_topics()
    print(lda.get_topics())
    for topic in topic_list:
        print(topic)
    for i in lda.get_document_topics(corpus)[:]:
        listj = []
        for j in i:
            listj.append(j[1])
        bz = listj.index(max(listj))
        print(i[bz][0])


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
def count_from_db(workId, country, platform, post_time, conn):
    sql = """
        select translated from raw_comment 
        where workId = {} and country = "{}" and platform = "{}"
        and postTime = "{}";
    """.format(workId, country, platform, post_time)
    comments = pd.read_sql(sql, conn)
    # print(comments)
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
    sql_query = """
        select * from word_freq_analy where workId = {} and country = "{}"
        and platform = "{}" and time = "{}";
    """.format(workId, country, platform, post_time)
    sql_delete = """
        delete from word_freq_analy where workId = {} and country = "{}"
        and platform = "{}" and time = "{}";
    """.format(workId, country, platform, post_time)
    cursor = conn.execute(text(sql_query)).cursor
    if len(cursor.fetchall()) > 0:
        conn.execute(text(sql_delete))
    sql_insert = """
                insert into word_freq_analy(workId, country, platform,
                time, polarity, keywords, frequency) values({}, "{}", "{}", "{}", "{}", "{}", "{}");
            """.format(workId, country, platform, post_time,
                       res_tuple[0], res_tuple[1], res_tuple[2])
    try:
        conn.execute(text(sql_insert))
        # print("写入数据库")
        conn.commit()  # 提交修改
        # print("插入成功")
    except (SQLAlchemyError, ProgrammingError):
        print("插入失败，有错误")
    finally:
        cursor.close()
    # print(len(cursor.fetchall()))


def count_words_by_workId(workId):
    conn = db_engine.connect()
    load_prefer_word_dict()  # 加载自定义词汇表
    print("加载自定义词汇")
    sql1 = "select distinct country, platform, postTime from raw_comment where workId = %d" % workId
    # 分别获取workId号作品的评论所属的国家列表、平台列表、发布时间列表
    df = pd.read_sql(sql1, con=conn)
    # print(countries)
    # print(platforms)
    # print(post_times)
    for i in range(len(df)):
        count_from_db(workId, df["country"][i], df["platform"][i], df["postTime"][i], conn)

    conn.close()
    del conn
    return True


def compute_matrix(df: pd.DataFrame):
    reviews = df["translated"].tolist()
    content = []
    for review in reviews:
        div_words = extract_term(seg_depart(review))  # 提取评论的主题词
        if len(div_words.strip()) > 0:
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
    # print(keywords)
    # freq = word_fre[:high_freq_word_num].tolist()
    # freq = list(map(lambda x: str(x), freq))
    # print(word_fre)
    # print(' '.join(keywords))
    # print(' '.join(freq))
    # print(word_fre)
    matrix = np.zeros((len(keywords) + 1) * (len(keywords) + 1)).reshape(len(keywords) + 1, len(keywords) + 1).astype(
        str)
    # print(matrix)
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
    sess = get_db_session()
    conn = sess.connection()
    sql_query = """
        select translated from raw_comment
        where workId = {} 
    """.format(workId)
    if country != "" and country != "全球":
        sql_query += ' and country = "{}" '.format(country)
    if post_time != "":
        sql_query += ' and postTime = "{}" '.format(post_time)
    res_data = pd.read_sql(sql=sql_query, con=conn)
    if len(res_data) == 0:
        return {"nodes": [], "edges": []}
    gram_matrix = compute_matrix(res_data)
    # gram_matrix.index = gram_matrix.iloc[:, 0].tolist()
    # print(gram_matrix)
    print(len(gram_matrix))
    if len(gram_matrix) <= 1:
        return {"nodes": [], "edges": []}
    word_names = gram_matrix[0].tolist()[1:]
    # print(word_names)
    aja_table = []
    node_num = min(len(word_names), 25)
    for i in range(1, node_num+1):
        for j in range(i + 1, node_num + 1):
            val = int(gram_matrix.iloc[i, j])
            if val > 0:
                aja_table.append([word_names[i-1], word_names[j-1], val])
    sess.commit()
    sess.close()
    del sess
    # 返回结点列表，即关键词 和 邻接表
    return {"nodes": word_names, "edges": aja_table}


def lda_test():
    conn = db_engine.connect()
    sql_query = """
            select translated from raw_comment
            where workId = 4 and country = "美国"
        """
    res_data = pd.read_sql(sql=sql_query, con=conn)
    lda_extract_terms(res_data)
    conn.close()
    del conn


if __name__ == "__main__":
    # load_prefer_word_dict()
    # res = seg_depart("纵观中国科幻电影，《流浪地球2》无疑是破天荒的存在。不过从两个纬度——电影制作、科幻品位来分析，寻找优秀之余的缺憾，才是批评的价值。电影在这两个范畴内都存在着诸多缺失。 （1）制作 面子十足，里子不足。 面子是声光画和娱乐性，里子是剧情台本和剪辑。 娱乐性此处指...  ")
    # print(res)
    # print(extract_term(res))
    # print(gather_info(res))
    # count_from_db(4, "中国", "豆瓣", "2023-01-2")
    # count_words_by_workId(19)
    res = generate_gram_matrix(4, "中国", "2023-01-23")
    print(res)
    # lda_test()
    pass
