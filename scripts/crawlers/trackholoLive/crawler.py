# -- coding: utf-8 --
import re

import requests, js2py
from bs4 import BeautifulSoup
from requests.packages import urllib3

# import matplotlib.pyplot as plt
# import matplotlib.dates as md
# from matplotlib.dates import HOURLY
# import numpy as np

requests.packages.urllib3.disable_warnings()
url = "https://trackholo.live/"

belongings = {
    'ときのそら': '0期生', 'ロボ子さん': '0期生', 'さくらみこ': '0期生', '星街すいせい': '0期生',
    '夜空メル': '1期生', 'アキ・ローゼンタール': '1期生', '赤井はあと': '1期生', '白上フブキ': '1期生', '夏色まつり': '1期生',
    '湊あくあ': '2期生', '紫咲シオン': '2期生', '百鬼あやめ': '2期生', '癒月ちょこ': '2期生', '大空スバル': '2期生',
    '兎田ぺこら': '3期生', '潤羽るしあ': '3期生', '不知火フレア': '3期生', '白銀ノエル': '3期生', '宝鐘マリン': '3期生',
    '天音かなた': '4期生', '桐生ココ': '4期生', '角巻わため': '4期生', '常闇トワ': '4期生', '姫森ルーナ': '4期生',
    '雪花ラミィ': '5期生', '桃鈴ねね': '5期生', '獅白ぼたん': '5期生', '魔乃アロエ': '5期生', '尾丸ポルカ': '5期生',
    '大神ミオ': 'ゲーマーズ', '猫又おかゆ': 'ゲーマーズ', '戌神ころね': 'ゲーマーズ',
    'AZKi': 'イノナカミュージック',
    '森美声': 'English', '小鳥遊キアラ': 'English', '一伊那尓栖': 'English', 'がうる・ぐら': 'English', 'ワトソン・アメリア': 'English',
    'アイラニ・イオフィフティーン': 'インドネシア', 'ムーナ・ホシノヴァ': 'インドネシア', 'アユンダ・リス': 'インドネシア',
    'クレイジー・オリー': 'インドネシア2期生', 'アーニャ・メルフィッサ': 'インドネシア2期生', 'パヴォリア・レイネ': 'インドネシア2期生',
    'アイリス': 'English Project:HOPE',
    '九十九佐命': 'English -議会-', 'セレス・ファウナ': 'English -議会-', 'オーロ・クロニー': 'English -議会-', '七詩ムメイ': 'English -議会-',
    'ハコス・ベールズ': 'English -議会-',
}


def get_data_by_member(name:str, t, output_full=False, output_24h=True):
    """
    Get data from https://trackholo.live containing youtube channel subscriber count,
    Example usage: get_data_by_member('minatoaqua',None,False,True)
    :param name: Hololive talent name(in romanji, without spaced)
    :param t: temporaily unused
    :param output_full: Output full subscriber variant json from debut
    :param output_24h: Output 24-h channel subscribe json file
    :return:
    """
    req = requests.get(f"https://trackholo.live/member/?name={name}")
    soup = BeautifulSoup(req.text, 'html.parser')
    js = soup.find(name="script", attrs={"type": "text/javascript"})
    ctx = js2py.EvalJs()
    pattern = re.compile(r'<[^>]+>', re.S)
    jstxt = pattern.sub('', str(js)).strip()
    # print(jstxt)
    # patch object
    ctx.execute(js="""
    const twemoji = {parse:function(a){}}
    const document = {body:null}
    const make_graph = function(){}
    const make_single_graph = function(){}
    const make_mixed_graph = function(){}
    function PerfectScrollbar(){}
    """)
    ctx.execute(jstxt)

    print(ctx.data_subscriber_all_series)
    # print(ctx.data_subscriber_24hours_series)
    # print(ctx.data_subscriber_24hours_labels)
    import json
    if output_full:
        with open(f"./{name}.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(list(ctx.data_subscriber_all_series)))
    x = list(ctx.data_subscriber_24hours_labels)
    y = [i["data"] for i in ctx.data_subscriber_24hours_series if "name" in i and i["name"] == 'チャンネル登録者数'][0]
    # print(x)
    # print(y)
    k = dict(zip(x, y))
    nlist = []
    for kk in k.keys():
        nlist.append({"x": kk, "y": k.get(kk)})
    # print(nlist)
    if output_24h:
        with open(f"./{name}-24h.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(nlist))
    else:
        print(nlist)
    # locator = md.AutoDateLocator(minticks=20)
    # locator.intervald[HOURLY] = [1]
    # fig = plt.figure(figsize=(21, 7))
    # ax = fig.add_subplot()
    # ax.xaxis.set_major_locator(locator=locator)
    # ax.plot(x, y)
    #
    # fig.autofmt_xdate()
    # plt.xlabel("data -24h")
    # plt.ylabel("チャンネル登録者数")
    #
    # plt.show()


if __name__ == '__main__':
    for member in ["ourokuronii","ceresfauna","nanashimumei","hakosbaelz","tsukumosana"]:
        get_data_by_member(member, "subscriber_all", output_full=True, output_24h=True)
