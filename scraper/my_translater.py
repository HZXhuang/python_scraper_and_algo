import requests
import time
import hashlib
import uuid

youdao_url = 'https://openapi.youdao.com/api'  # 有道api地址


def base_translate(translate_text, to_lang="zh-CHS"):
    # 翻译文本生成sign前进行的处理
    input_text = ""

    # 当文本长度小于等于20时，取文本
    if len(translate_text) <= 20:
        input_text = translate_text

    # 当文本长度大于20时，进行特殊处理
    elif len(translate_text) > 20:
        input_text = translate_text[:10] + str(len(translate_text)) + translate_text[-10:]

    time_curtime = int(time.time())  # 秒级时间戳获取
    app_id = "25d9966a21c59aae"  # 应用id
    uu_id = uuid.uuid4()  # 随机生成的uuid数，为了每次都生成一个不重复的数。
    app_key = "NajZLqXjs9gxGJfDEx8OfD1A7rMrwwpW"  # 应用密钥

    sign = hashlib.sha256(
        (app_id + input_text + str(uu_id) + str(time_curtime) + app_key).encode('utf-8')).hexdigest()  # sign生成

    data = {
        'q': translate_text,  # 翻译文本
        # 'from': "en",  # 源语言
        'to': to_lang,  # 翻译语言
        'appKey': app_id,  # 应用id
        'salt': uu_id,  # 随机生产的uuid码
        'sign': sign,  # 签名
        'signType': "v3",  # 签名类型，固定值
        'curtime': time_curtime,  # 秒级时间戳
    }

    r = requests.get(youdao_url, params=data).json()  # 获取返回的json()内容
    try:
        res = r["translation"][0]
        if len(res.strip()) == 0:
            return translate_text
        return res
    except (KeyError, IndexError):
        return translate_text


def youdao_translate(translate_text):
    return base_translate(translate_text, "zh-CHS")


def translate_to_en(text):
    return base_translate(text, "en")


if __name__ == "__main__":
    # print(youdao_translate("hello"))
    print(translate_to_en("哪吒之魔童降世"))
    pass
