from sql_dao import db_engine
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError


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
    insert into raw_comment(content, translated, likes, workId, sentiment, country, platform, postTime) 
    values("{}", "{}", {}, {}, "{}", "{}", "{}", "{}");
"""

# cursor = conn.cursor()
query_sql = """
    select * from user;
"""
# df = pd.read_sql(query_sql, con=conn)
# print(df)


def insert_comment(content, translated, likes, workId, sentiment, country, platform, postTime):
    conn = db_engine.connect()
    translated = translated.replace("\"", "'")
    try:
        conn.execute(text(insert_comment_sql.format(content, translated, likes, workId,
                                                    sentiment, country, platform, postTime)))
        conn.commit()
        return True
    except ProgrammingError:
        print("sql语法错误")
        return False
    finally:
        conn.close()
        del conn


if __name__ == "__main__":
    # print(insert_comment_sql.format("真实一部好电影", "30", 1, "正面", "美国", "Youtube", "2020-05-23"))
    insert_comment("This is a' \"good movie", "中共那來的量子連晶片都沒有還吹牛作夢吧....流浪地球2我也", "30", 1, "积极", "美国", "Youtube", "-05-23")
