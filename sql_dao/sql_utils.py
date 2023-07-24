import pymysql
import pandas as pd
from sql_dao import host, port, username, password, database, charset

conn = pymysql.connect(
    host=host,
    port=port,
    user=username,
    password=password,
    database=database,
    charset=charset
)

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
    cursor = conn.cursor()
    cursor.execute(insert_comment_sql.format(content, translated, likes, workId, sentiment, country, platform, postTime))
    conn.commit()
    cursor.close()


if __name__ == "__main__":
    # print(insert_comment_sql.format("真实一部好电影", "30", 1, "正面", "美国", "Youtube", "2020-05-23"))
    insert_comment("This is a' good movie", "真实一部好电影", "30", 1, "积极", "美国", "Youtube", "2020-05-23")
