from httplib2 import socks, ProxyInfo, Http
import numpy as np
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import json
import pycountry
from scraper import base_path
from scraper import my_utils
from scraper import nameMap
from sql_dao.sql_utils import insert_comment
from scraper.my_translater import youdao_translate

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
platform = "Youtube"

DEVELOPER_KEY = 'AIzaSyAp0oxZY8Sa6avNrEAmU3JZCKwW1_-okik'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# 设置http代理，
proxy_info = ProxyInfo(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 1080)
http = Http(timeout=30, proxy_info=proxy_info)


# 调用Youtube API的 channels.list 方法获取频道所属的国家
def list_channel_country(youtube, channel_id, comment):
    results = youtube.channels().list(
        part='snippet',
        id=channel_id
    ).execute()

    if 'country' in results['items'][0]['snippet']:
        country = results['items'][0]['snippet']['country']
        return nameMap[pycountry.countries.get(alpha_2=country).name]
    else:
        return my_utils.identify_lang_to_country(comment)


def get_comments(keyword, max_results, max_comment_cnt, workId):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
                    developerKey=DEVELOPER_KEY, http=http)

    search_response = youtube.search().list(  # 根据搜索关键词查询匹配的视频id
        q=keyword,
        part='id,snippet',
        maxResults=max_results
    ).execute()
    videos = []
    for search_result in search_response.get('items', []):
        if search_result['id']['kind'] == 'youtube#video':
            temp = {}
            temp["title"] = search_result['snippet']['title']
            temp["video_id"] = search_result['id']['videoId']
            videos.append(temp)
    videos_json = json.dumps(videos, indent=4, ensure_ascii=False)
    with open(base_path + '/out/{}视频id_{}.json'.format(keyword, platform), 'w', encoding='utf-8') as f:
        f.write(videos_json)
    comments = []
    count = 0
    video_cnt = 0
    try:
        for video in videos:
            video_cnt += 1
            videoId = video["video_id"]
            try:
                request = youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=videoId,
                    maxResults=max_comment_cnt
                )
                # print(comments)
                print("爬取第{}个视频的评论".format(video_cnt))
                response = request.execute()

                totalResults = int(response['pageInfo']['totalResults'])
                nextPageToken = ''

                first = True
                further = True
                while further:
                    halt = False
                    if not first:
                        print('..')
                        try:
                            response = youtube.commentThreads().list(
                                part="snippet,replies",
                                videoId=videoId,
                                maxResults=max_comment_cnt,
                                textFormat='plainText',
                                pageToken=nextPageToken
                            ).execute()
                            totalResults = int(response['pageInfo']['totalResults'])
                        except HttpError as e:
                            print("An HTTP error %d occurred:\n%s" % (e.resp.status, e.content))
                            halt = True

                    if halt == False:
                        count += totalResults
                        for item in response["items"]:
                            # This is only a part of the data.
                            # You can choose what you need. You can print the data information you can get and crawl it as needed.
                            comment = item["snippet"]["topLevelComment"]
                            # author = comment["snippet"]["authorDisplayName"]
                            text = my_utils.text_clean(comment["snippet"]["textDisplay"])
                            likeCount = comment["snippet"]['likeCount']
                            publishtime = comment['snippet']['publishedAt']
                            # channelId = comment['snippet']['authorChannelId']["value"]
                            country = my_utils.identify_lang_to_country(text)
                            if country != "中国":
                                translated = youdao_translate(text)
                            else:
                                translated = text
                            insert_comment(text, translated, likeCount, workId,
                                           my_utils.analyze_polarity(translated), country, platform, publishtime)
                            comments.append([text, translated, likeCount, workId,
                                             my_utils.analyze_polarity(translated), country, platform, publishtime])
                        if totalResults < max_comment_cnt:  # 获取的最大评论数
                            further = False
                        else:
                            further = True
                            first = False
                            try:
                                nextPageToken = response["nextPageToken"]
                            except KeyError as e:
                                print("An KeyError error occurred: %s" % e)
                                further = False
            except HttpError as e:
                print("An HttpError error occurred: %s" % e)
    except ConnectionResetError as e:
        print("远程主机强迫关闭了一个现有的连接：%s" % e)
    print('get data count: ', str(count))

    ### write to csv file
    data = np.array(comments)
    df = pd.DataFrame(data, columns=['content', 'translated', 'likes', 'workId',
                                     'sentiment', 'country', 'platform', 'postTime'])
    df.to_csv(base_path + '/out/{}_{}.csv'.format(keyword, platform), index=0, encoding='utf-8')

    ### write to json file
    # result = []
    # for time, vote, country, comment in comments:
    #     temp = {}
    #     temp['publishtime'] = time
    #     temp['likeCount'] = vote
    #     temp['country'] = country
    #     temp['comment'] = comment
    #     result.append(temp)
    # print('result: ', len(result))
    #
    # json_str = json.dumps(result, indent=4, ensure_ascii=False)
    # with open('./data/{}评论.json'.format(keyword), 'w', encoding='utf-8') as f:
    #     f.write(json_str)


if __name__ == "__main__":
    # get_comments("红楼梦", 15, 200)
    insert_comment("真实一部好电影", "好电影", "30", 1, "积极", "美国", "Youtube", "2020-05-23")
