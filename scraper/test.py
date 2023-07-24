import os
from scraper import base_path
import pandas as pd
import datetime


def save_file():
    print(base_path)
    # with open("/static/my.txt", "w", encoding="utf-8") as f:
    #     f.write("你好")


if __name__ == "__main__":
    # save_file()
    # print(os.listdir(base_path))
    print(datetime.datetime.now() - pd.Timedelta(weeks=2))
    pass
