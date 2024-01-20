import os
from scraper import base_path
from scraper.my_utils import identify_lang
import emoji
import pandas as pd
from sql_dao.sql_utils import db_engine, text


def save_file():
    print(base_path)
    # with open("/static/my.txt", "w", encoding="utf-8") as f:
    #     f.write("你好")


def lang_detect():
    conn = db_engine.connect()
    query_sql = "select * from raw_comment"
    update_sql = "update raw_comment set language = '{}' where id = {}"
    df = pd.read_sql(query_sql, conn)
    for i in range(len(df)):
        ID = df.iloc[i]["id"]
        content = df.iloc[i]["content"]
        lang = identify_lang(content)
        conn.execute(text(update_sql.format(lang, ID)))
    conn.commit()
    conn.close()


if __name__ == "__main__":
    # save_file()
    # print(os.listdir(base_path))
    # print(datetime.datetime.now() - pd.Timedelta(weeks=2))
    # text = "解说很好，就是广告太多了😢很不错❤❤❤🌹🌹🌹👍 😂 😭😭😭😭❤🎉😂🎉🎉❤❤🤣❤️🫰"
    # print(emoji.replace_emoji(text, ""))
    # df = pd.read_csv("./out/流浪地球2_Youtube.csv", sep="|", encoding="utf-8")
    # print(df)
    lang_detect()
    pass
