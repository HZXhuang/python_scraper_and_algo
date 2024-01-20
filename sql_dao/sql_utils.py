from sql_dao import db_engine
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError, StatementError


# def get_conn():
#     conn = pymysql.connect(
#         host=host,
#         port=port,
#         user=username,
#         password=password,
#         database=database,
#         charset=charset,
#     )
#     return conn


insert_comment_sql = """
    insert into raw_comment(content, translated, language, likes, workId, sentiment, country, platform, postTime) 
    values("{}", "{}", "{}", {}, {}, "{}", "{}", "{}", "{}");
"""

insert_work_score_sql = """
    insert into work_score(workId, score, platform) values({}, {}, "{}");
"""

insert_work_sql = """
    insert into monitor_work(name, category, labels, citeUrl, imgUrl, content, postTime) 
    values("{}", "{}", "{}", "{}", "{}", "{}", "{}");
"""

insert_recommend_work_sql = """
    insert into recommend_work(userId, workId, score) values({}, {}, {});
"""

# cursor = conn.cursor()
# df = pd.read_sql(query_sql, con=conn)
# print(df)


def insert_comment(content, translated, language, likes, workId, sentiment, country, platform, postTime):
    conn = db_engine.connect()
    content = content.replace("\"", "")
    translated = translated.replace("\"", "'")
    try:
        conn.execute(text(insert_comment_sql.format(content, translated, language, likes, workId,
                                                    sentiment, country, platform, postTime)))
        conn.commit()
        return True
    except (ProgrammingError, StatementError):
        print("sql语法错误")
        return False
    finally:
        conn.close()
        del conn


def insert_work_score(workId, score, platform):
    conn = db_engine.connect()
    try:
        conn.execute(text(insert_work_score_sql.format(workId, score, platform)))
        conn.commit()
        return True
    except (ProgrammingError, StatementError):
        print("sql语法错误")
        return False
    finally:
        conn.close()
        del conn


def insert_work(name, category, label, workUrl, imgUrl, content, postTime):
    conn = db_engine.connect()
    content = content.replace("\"", "")
    # cursor = conn.cursor()
    try:
        conn.execute(text(insert_work_sql.format(name, category, label, workUrl, imgUrl, content, postTime)))
        conn.commit()
        return True
    except (ProgrammingError, StatementError):
        print("sql语法错误")
        return False
    finally:
        conn.close()
        del conn


def insert_recommend_work(userId, workId, score, conn):
    try:
        conn.execute(text(insert_recommend_work_sql.format(userId, workId, score)))
        conn.commit()
        return True
    except (ProgrammingError, StatementError):
        print("sql语法错误")
        return False


# 删除重复的评论
def detect_duplicated_comment(workId, country, platform, postTime, content):
    conn = db_engine.connect()
    content = content.replace("\"", "")
    select_sql = 'select * from raw_comment where workId = {} and country = "{}" and platform = "{}" and ' \
                 'postTime = "{}" and content = "{}"'.format(workId, country, platform, postTime, content)
    # delete_sql = 'delete from raw_comment where workId = {} and country = "{}" and platform = "{}" and ' \
    #              'postTime = "{}" and content = "{}"'.format(workId, country, platform, postTime, content)
    try:
        res = conn.execute(text(select_sql)).cursor.fetchone()
    except (ProgrammingError, StatementError):
        return True
    finally:
        conn.close()

    if res is not None:
        print(res)
        return True
    else:
        return False


if __name__ == "__main__":
    # print(insert_comment_sql.format("真实一部好电影", "30", 1, "正面", "美国", "Youtube", "2020-05-23"))
    # insert_comment("This is a' \"good movie", "中共那來的量子連晶片都沒有還吹牛作夢吧....流浪地球2我也", "30", 1, "积极", "美国", "Youtube", "-05-23")
    # insert_work('流浪地球', '影视', '科幻 动作', '111', '111', '222', '2020-02-01')

    res = detect_duplicated_comment(1, "中国", "豆瓣", "2024-01-01", "评论")
    print(res)
    pass
