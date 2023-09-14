import gc

from flask import Flask, jsonify, request
from scraper.my_utils import check_exists_and_make_dir
from scraper.youtube_scraper import scrap_reviews as scrap_reviews_youtube
from scraper.facebook_scraper import scrap_reviews as scrap_reviews_facebook
from scraper.twitter_scraper import scrap_reviews as scrap_reviews_twitter
from scraper.douban_scraper import scrap_reviews as scrap_reviews_douban
from scraper.IMDb_scraper import scrap_reviews as scrap_reviews_imdb
from scraper.goodreads_scraper import scrap_reviews as scrap_reviews_goodreads
from scraper.rottentomatoes_scraper import scrap_reviews as scrap_reviews_tomatoes
from scraper.amazon_scraper import scrap_reviews as scrap_reviews_amazon
from scraper.amazon_score_scraper import scrap_score as scrap_score_amazon
from scraper.douban_score_scraper import scrap_score as scrap_score_douban
from scraper.goodreads_score_scraper import scrap_score as scrap_score_goodreads
from scraper.rottentomatoes_score_scraper import scrap_score as scrap_score_tomatoes
from scraper.imdb_score_scraper import scrap_score as scrap_score_imdb
from analyzer.word_statistics import generate_gram_matrix, count_words_by_workId
from recommend.work_recommend import recommend


app = Flask(__name__)
check_exists_and_make_dir("out")
check_exists_and_make_dir("profile")


def success(data=None):
    json_res = {
        "code": "0",
        "msg": "响应成功",
        "data": data
    }
    return jsonify(json_res)


def err_res(msg, code=-1):
    json_res = {
        "code": str(code),
        "msg": msg,
        "data": None
    }
    return jsonify(json_res)


@app.route('/')
def hello_world():  # put application's code here
    return success()


# 爬取Facebook评论
@app.route('/scrap_facebook', methods=["GET"])
def scrap_facebook():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_facebook(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取推特评论
@app.route('/scrap_twitter', methods=["GET"])
def scrap_twitter():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_twitter(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取Youtube评论
@app.route('/scrap_youtube', methods=["GET"])
def scrap_youtube():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_youtube(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取亚马逊评论
@app.route('/scrap_amazon', methods=["GET"])
def scrap_amazon():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_amazon(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取豆瓣评论
@app.route('/scrap_douban', methods=["GET"])
def scrap_douban():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_douban(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取GoodReads评论
@app.route('/scrap_goodreads', methods=["GET"])
def scrap_goodreads():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_goodreads(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取IMDB评论
@app.route('/scrap_imdb', methods=["GET"])
def scrap_imdb():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_imdb(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取烂番茄评论
@app.route('/scrap_tomato', methods=["GET"])
def scrap_tomato():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_reviews_tomatoes(keyword, workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取烂番茄评分
@app.route('/scrap_tomato_score', methods=["GET"])
def scrap_tomato_score():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_score_tomatoes(workId, keyword)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取豆瓣评分
@app.route('/scrap_douban_score', methods=["GET"])
def scrap_douban_score():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_score_douban(workId, keyword)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取IMDb评分
@app.route('/scrap_IMDb_score', methods=["GET"])
def scrap_IMDb_score():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_score_imdb(workId, keyword)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取亚马逊评分
@app.route('/scrap_amazon_score', methods=["GET"])
def scrap_amazon_score():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_score_amazon(workId, keyword)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 爬取GoodReads评分
@app.route('/scrap_goodreads_score', methods=["GET"])
def scrap_goodreads_score():
    args = request.args
    keyword = args.get("keyword", default="", type=str)
    workId = args.get("workId", default=0, type=int)
    if not keyword:
        return err_res("请输入关键词")
    if workId == 0:
        return err_res("请输入监测作品ID")
    res = scrap_score_goodreads(workId, keyword)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("爬取失败")


# 生成共现语义网络图的api接口，
@app.route('/generate_network', methods=["GET"])
def generate_network():
    args = request.args
    workId = args.get("workId", default=0, type=int)
    country = args.get("country", default="", type=str)
    post_time = args.get("post_time", default="", type=str)
    gc.collect()
    if workId == 0:
        return err_res("请输入作品ID")
    return success(generate_gram_matrix(workId, country, post_time))


# 关键词提取、词性分析和词频统计的接口
@app.route("/words_freq_sta", methods=["GET"])
def words_freq_sta():
    args = request.args
    workId = args.get("workId", default=0, type=int)
    if workId == 0:
        return err_res("请输入作品ID")
    res = count_words_by_workId(workId)
    gc.collect()
    if res:
        return success()
    else:
        return err_res("系统出现错误，请重试！")


# 个性化推荐接口
@app.route("/recommend", methods=["GET"])
def person_recommend():
    res = recommend()
    if res:
        return success()
    else:
        return err_res("系统出现错误，请重试！")


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5050)
