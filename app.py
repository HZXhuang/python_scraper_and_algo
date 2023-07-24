from flask import Flask, jsonify, request
from scraper.my_utils import check_exists_and_make_dir
import scraper.youtube_scraper as youtube_sp
import scraper.twitter_scraper as twitter_sp
import scraper.facebook_scraper as facebook_sp
import scraper.amazon_scraper as amazon_sp
import scraper.douban_scraper as douban_sp
import scraper.goodreads_scraper as goodreads_sp
import scraper.IMDb_scraper as imdb_sp
import scraper.rottentomatoes_scraper as tomato_sp

app = Flask(__name__)
check_exists_and_make_dir("out")
check_exists_and_make_dir("profile")
print("hello world")


@app.route('/')
def hello_world():  # put application's code here
    json_output = {
        "code": 0,
        "msg": "响应成功",
        "data": [

        ]
    }
    return jsonify(json_output)


@app.route('/scrap_facebook', methods=["GET"])
def scrap_facebook():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = facebook_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_twitter', methods=["GET"])
def scrap_twitter():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = twitter_sp.scrap_twitter(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_youtube', methods=["GET"])
def scrap_youtube():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = youtube_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_amazon', methods=["GET"])
def scrap_amazon():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = amazon_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_douban', methods=["GET"])
def scrap_douban():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = douban_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_goodreads', methods=["GET"])
def scrap_goodreads():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = goodreads_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_imdb', methods=["GET"])
def scrap_imdb():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = imdb_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


@app.route('/scrap_tomato', methods=["GET"])
def scrap_tomato():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return "请输入关键词"
    if workId == 0:
        return "请输入监测作品ID"
    res = tomato_sp.scrap_reviews(keyword, workId)
    if res:
        return "爬取成功"
    else:
        return "爬取失败"


if __name__ == '__main__':
    app.run()
