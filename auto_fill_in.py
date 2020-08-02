# -*-coding:utf-8-*-
import sys
import os
from bs4 import BeautifulSoup
import requests
from PIL import Image, ImageEnhance
import execjs
import time
import codecs
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
import matplotlib.pyplot as plt

requests.packages.urllib3.disable_warnings()
requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += 'HIGH:!DH:!aNULL'
try:
    requests.packages.urllib3.contrib.pyopenssl.DEFAULT_SSL_CIPHER_LIST += 'HIGH:!DH:!aNULL'
except AttributeError:
    # no pyopenssl support used / needed / available
    pass
ua = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    'Host': 'jwxt.bupt.edu.cn',
    'Origin': 'https://jwxt.bupt.edu.cn'
}


def encodepw(username, password):
    from base64 import b64encode
    return (b64encode(str.encode(username)) + b"%%%" + b64encode(str.encode(password))).decode()


def login_new(username, password):
    url = "http://jwgl.bupt.edu.cn/jsxsd/"
    ua['Host'] = "jwgl.bupt.edu.cn"
    ua['Accept'] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8," \
                   "application/signed-exchange;v=b3;q=0.9 "
    del ua['Origin']
    html = requests.get(url=url, headers=ua)  # 获得登录页面
    if html.status_code != 200:
        print(f"[+] GET page failed! Status code:{html.status_code}")
        return
    print("[*] GET jiaowu page success!")
    # print(html.content)
    url_auth = "http://jwgl.bupt.edu.cn/jsxsd/xk/LoginToXk"
    ua['Origin'] = "http://jwgl.bupt.edu.cn"
    data = {
        "userAccount": username,
        "userPassword": "",
        "encoded": encodepw(username, password)
    }
    print(data)
    s = requests.session()
    html_in = s.post(url=url_auth, headers={"Referer": "http://jwgl.bupt.edu.cn/jsxsd/",
                                            "Origin": "http://jwgl.bupt.edu.cn", }, data=data)
    with open("get1.html", "wb")as f:
        f.write(html_in.content)
    sign = f"var userid = {username}"
    if str.encode(sign) not in html_in.content:
        print("[+] Login failed!")
        return
    # jw_html = requests.get(url="http://jwgl.bupt.edu.cn/jsxsd/framework/xsMain.jsp", headers=ua)
    # # print(jw_html.content)
    print("[*] Login success!")
    s.headers.update({'Referer': "http://jwgl.bupt.edu.cn/jsxsd/framework/xsMain.jsp"})
    del ua['Origin']
    kb_html = s.get(url="http://jwgl.bupt.edu.cn/jsxsd/xskb/xskb_list.do", headers=ua)
    kb_html.encoding = "utf-8"

    soup = BeautifulSoup(kb_html.text, 'html.parser')
    if "学期理论课表" not in soup.title:
        print("[+] Load Class table webpage failed!")
        return
    form = soup.select("#Form1")[0]
    x = form.find_all(["input", "select"])
    datas = {}
    for a in x:
        if a.get("name") is not None:
            if a.get("value") is not None:
                datas.setdefault(a.get("name"), []).append(a.get("value"))
            else:
                datas.update({a.get("name"): [c for c in a.contents if c not in ('\n', '\r\n')][0].get('value')})
    for key in datas.keys():
        if isinstance(datas[key], list):
            if len(datas[key]) == 1:
                datas.update({key: datas[key][0]})
    kb_html = s.post(url="http://jwgl.bupt.edu.cn/jsxsd/xskb/xskb_list.do", data=datas)
    '''
    cj0701id: 
    zc:  select
    demo:  
    xnxq01id: 2019-2020-1  select
    sfFD: 1
    kbjcmsid: 9475847A3F3033D1E05377B5030AA94D  select
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-1-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-1-2
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-2-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-2-2
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-3-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-3-2
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-4-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-4-2
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-5-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-5-2
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-6-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-6-2
    jx0415zbdiv_1: A73306CD9B4B438F8F8666870F41A417-7-1
    jx0415zbdiv_2: A73306CD9B4B438F8F8666870F41A417-7-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-1-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-1-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-2-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-2-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-3-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-3-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-4-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-4-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-5-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-5-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-6-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-6-2
    jx0415zbdiv_1: 1429023BE5DB4F8B957F360E6C421F04-7-1
    jx0415zbdiv_2: 1429023BE5DB4F8B957F360E6C421F04-7-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-1-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-1-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-2-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-2-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-3-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-3-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-4-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-4-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-5-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-5-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-6-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-6-2
    jx0415zbdiv_1: 7E33D6BF8F3640EB9A77F3592466011F-7-1
    jx0415zbdiv_2: 7E33D6BF8F3640EB9A77F3592466011F-7-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-1-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-1-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-2-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-2-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-3-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-3-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-4-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-4-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-5-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-5-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-6-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-6-2
    jx0415zbdiv_1: 0ABB576C8E844E09AEC9ED976614F814-7-1
    jx0415zbdiv_2: 0ABB576C8E844E09AEC9ED976614F814-7-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-1-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-1-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-2-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-2-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-3-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-3-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-4-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-4-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-5-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-5-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-6-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-6-2
    jx0415zbdiv_1: 7B5933ECABB9486E9985C90A32A1BFAE-7-1
    jx0415zbdiv_2: 7B5933ECABB9486E9985C90A32A1BFAE-7-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-1-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-1-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-2-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-2-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-3-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-3-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-4-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-4-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-5-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-5-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-6-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-6-2
    jx0415zbdiv_1: 85CFD335A1C346B6A4384F111455D578-7-1
    jx0415zbdiv_2: 85CFD335A1C346B6A4384F111455D578-7-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-1-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-1-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-2-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-2-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-3-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-3-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-4-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-4-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-5-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-5-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-6-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-6-2
    jx0415zbdiv_1: 5A327152B30240A59DC2E755F0A815D5-7-1
    jx0415zbdiv_2: 5A327152B30240A59DC2E755F0A815D5-7-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-1-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-1-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-2-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-2-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-3-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-3-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-4-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-4-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-5-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-5-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-6-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-6-2
    jx0415zbdiv_1: 75639017F2EB427CB7602902E7F55326-7-1
    jx0415zbdiv_2: 75639017F2EB427CB7602902E7F55326-7-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-1-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-1-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-2-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-2-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-3-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-3-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-4-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-4-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-5-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-5-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-6-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-6-2
    jx0415zbdiv_1: 147D6B22ED7949C09227EBF069E24A45-7-1
    jx0415zbdiv_2: 147D6B22ED7949C09227EBF069E24A45-7-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-1-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-1-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-2-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-2-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-3-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-3-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-4-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-4-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-5-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-5-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-6-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-6-2
    jx0415zbdiv_1: 6D8AACC5C29849229E0BFECDF87F2171-7-1
    jx0415zbdiv_2: 6D8AACC5C29849229E0BFECDF87F2171-7-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-1-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-1-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-2-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-2-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-3-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-3-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-4-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-4-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-5-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-5-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-6-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-6-2
    jx0415zbdiv_1: A1D2B61F65EB4A28B7F3CA3C067788B0-7-1
    jx0415zbdiv_2: A1D2B61F65EB4A28B7F3CA3C067788B0-7-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-1-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-1-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-2-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-2-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-3-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-3-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-4-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-4-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-5-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-5-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-6-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-6-2
    jx0415zbdiv_1: FA28FAB30A514608B0D2F1B7FA6A4A5F-7-1
    jx0415zbdiv_2: FA28FAB30A514608B0D2F1B7FA6A4A5F-7-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-1-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-1-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-2-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-2-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-3-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-3-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-4-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-4-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-5-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-5-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-6-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-6-2
    jx0415zbdiv_1: 61D404581ED240C2A188A57452512692-7-1
    jx0415zbdiv_2: 61D404581ED240C2A188A57452512692-7-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-1-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-1-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-2-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-2-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-3-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-3-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-4-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-4-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-5-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-5-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-6-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-6-2
    jx0415zbdiv_1: B47B1964D009486388F03DF44AF91DB8-7-1
    jx0415zbdiv_2: B47B1964D009486388F03DF44AF91DB8-7-2
    '''

    with open("get2.html", "wb") as f:
        f.write(kb_html.content)
        print("[*] Class table write to local file!")


'''
直接从教务系统入口登录(selenium)
'''


def login2(username, password, max_try=3, browser='-i', debug_use=True):
    if not debug_use:
        raise DeprecationWarning("this system is going to close down at 2020.8, login via old jwxt will be no longer "
                                 "available")
    url = 'https://jwxt.bupt.edu.cn/jwLoginAction.do'
    # print(browser)
    # browser = webdriver.Chrome(
    # executable_path=r"C:\\Users\Ren Ziheng\AppData\Local\Google\Chrome\Application\chromedriver.exe")
    if browser.lower() == '--chrome' or browser == '-c':
        try:
            browser = webdriver.Chrome()
        except WebDriverException as e:
            print(e.msg)
            print("\033[0;31m这个程序是基于Selenium编写的，你需要从http://chromedriver.storage.googleapis.com/index.html上下载"
                  "适合你浏览器的chromedriver.exe，并将chromedriver.exe复制到你的Chrome浏览器安装目录下，将浏览器安装目录"
                  "变量添加到path中，再把chromedriver.exe复制到python安装目录即可。"
                  "[参考http://www.bubuko.com/infodetail-2378684.html]\033[0;31m")
            return
    elif browser.lower() == '--ie' or browser == '-i':
        try:
            browser = webdriver.Ie()
        except WebDriverException as e:
            print(e.msg)
            print("\033[0;31m这个程序是基于Selenium编写的，你需要从https://selenium-release.storage.googleapis.com/index.html上下载适合你浏览器"
                  "的IEDriverServer.exe，并将其复制到你的ie浏览器安装目录下，将浏览器的安装目录添加到系统path中即可。"
                  "[参考https://github.com/SeleniumHQ/selenium/wiki/InternetExplorerDriver]\033[0;31m")
            return
    elif browser.lower() == '--edge' or browser == '-e':
        try:
            browser = webdriver.Edge()
        except WebDriverException as e:
            print(e.msg)
            print("\033[0;31m这个程序是基于Selenium编写的，你需要从http://go.microsoft.com/fwlink/?LinkId=619687上下载适合你浏览器版本的"
                  "MicrosoftWebDriver.exe，并将其复制到你的edge浏览器安装目录下，将浏览器的安装目录添加到系统path中即可。"
                  "[需要Windows10版本系统]\033[0;31m")
            return
    elif browser.lower() == '--firefox' or browser == '-f':
        try:
            browser = webdriver.Firefox()
        except WebDriverException:
            print("\033[0;31m这个程序是基于Selenium编写的，你需要从https://github.com/mozilla/geckodriver/releases上下载"
                  "适合你浏览器的geckodriver.exe，并将geckodriver.exe复制到你的浏览器安装目录下，将浏览器安装目录"
                  "变量添加到path中，再把geckodriver.exe复制到python安装目录即可。"
                  "[参考http://www.bubuko.com/infodetail-2378684.html]\033[0;31m")
            return
    for trial in range(0, max_try):
        browser.get(url)
        browser.refresh()
        browser.minimize_window()
        # print(browser.get_cookies())
        print("还剩{}次尝试".format(max_try - trial))
        usernameElem = browser.find_element_by_name("zjh")
        usernameElem.send_keys(username)

        passwordElem = browser.find_element_by_name('mm')
        passwordElem.send_keys(password)

        yzmElem = browser.find_element_by_name('v_yzm')

        browser.get_screenshot_as_file("./temp/screenshot.png")

        yzmchart = browser.find_element_by_id('vchart')
        location = yzmchart.location
        size = yzmchart.size
        left = location['x']
        top = location['y']
        right = location['x'] + size['width']
        bottom = location['y'] + size['height']
        im = Image.open("./temp/screenshot.png").crop((left, top, right, bottom))
        im = ImageEnhance.Contrast(im).enhance(2.0)
        im.save('./temp/code.png')
        im.load()
        im = Image.open("./temp/code.png")

        plt.figure(figsize=(3, 3))
        plt.ion()  # 打开交互模式
        plt.axis('off')  # 不需要坐标轴

        plt.imshow(im)
        plt.ioff()  # 显示完后一定要配合使用plt.ioff()关闭交互模式，否则可能出奇怪的问题
        plt.pause(5)
        code = input('Input the captcha code<type "quit" to terminate>:')
        if code == '"quit"':
            return
        while code.strip() == '':
            print("captcha code can not be empty!")
            code = input('Input the captcha code<type "quit" to terminate>:')

        yzmElem.clear()
        yzmElem.send_keys(code)
        print(yzmElem.get_attribute('value'))
        button = browser.find_element_by_id('btnSure')
        button.click()
        if "学分制综合教务" not in browser.title:
            if "error" in browser.page_source:
                browser.refresh()
            if trial < max_try - 1:
                if "你输入的校验码有误，请重新输入" in browser.page_source:
                    print("验证码输入错误")
                if "数据库忙请稍候再试" in browser.page_source:
                    print("教务系统数据库忙，请稍后再登录")
                plt.clf()  # 清空图片
                plt.close()  # 清空窗口
                trial += 1
                time.sleep(3)
                browser.refresh()
                continue
            else:
                plt.clf()  # 清空图片
                plt.close()  # 清空窗口
                print("登录失败，请稍后再试")
                return
        else:
            # 终于登录成功了！
            plt.clf()  # 清空图片
            plt.close()  # 清空窗口
            print("Login success")
            print("----------")
            break
            # browser.add_cookie({"JSESSIONID": cookie})
    
    browser.get("https://jwxt.bupt.edu.cn/xkAction.do?actionType=6")
    # print(browser.page_source)
    with codecs.open("./temp/{}_class.html".format(username), "w") as f:
        f.write(browser.page_source)
        print("class info get.")
    browser.get("https://jwxt.bupt.edu.cn/ksApCxAction.do?oper=getKsapXx")
    with open("./temp/{}_exam.html".format(username), "w", encoding='utf-8') as f:
        f.write(browser.page_source)
        print("exam info get.")
    browser.close()
    print("quit")


'''
直接从教务系统入口登录(requests)
'''


def login(username, password):
    url = 'https://jwxt.bupt.edu.cn/jwLoginAction.do'

    html = requests.get(url=url, headers=ua, verify=False)  # 获得登录页面
    print(html.headers)
    print(html.cookies)
    cookies = {
        "JSESSIONID": html.cookies.get("JSESSIONID")
    }
    # print(cookies)
    soup = BeautifulSoup(html.text, 'html.parser')
    # ua['Referer'] = url
    yzmchart = soup.select("#vchart")[0]  # 获得验证码

    random_num = execjs.eval("Math.random()")
    yzmurl = "https://jwxt.bupt.edu.cn{}{}".format(yzmchart['src'], random_num)
    sso = soup.find(name="input", attrs={"name": "type"})["value"]
    print(yzmurl)
    requests.utils.add_dict_to_cookiejar(html.cookies, cookies)
    s = requests.Session()
    code_headers = ua
    code_headers.update({
        "Referer": "https://jwxt.bupt.edu.cn/jwLoginAction.do",
        "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
    })
    with open("./temp/code.png", 'wb') as f:
        c = s.get(url=yzmurl, headers=code_headers, cookies=cookies)
        f.write(c.content)
    im = Image.open("./temp/code.png")
    im.show('code')
    code = input("Input the captcha code:")
    payload = {
        "type": sso,
        "zjh": username,
        "mm": password,
        "v_yzm": code
    }
    # print(payload)
    req = s.post(url=url, data=payload, headers=ua, verify=False, cookies=cookies)
    if req.status_code != requests.codes.OK:
        print(req.text)
    else:
        soup2 = BeautifulSoup(req.text, 'html.parser')
        print(req.content)
        noticeElem = soup2.strong.string
        # print(noticeElem)
        if "你输入的校验码有误，请重新输入" in noticeElem:
            print("验证码输错了")
        print("Please retry")


def login_from_portal(username, password):
    url_a = "http://auth.bupt.edu.cn/authserver/login"
    service_params = {
        "service": "http://my.bupt.edu.cn/index.portal"
    }
    # step1: 请求登录页，获得cookie(JSESSIONID)
    html = requests.get(url=url_a, params=service_params, headers=ua)
    cookies = {
        "JSESSIONID": html.cookies.get("JSESSIONID"),
    }
    print(cookies)
    '''
    1.
        lt:LT-542636-EdxVjZK9gtP2eTg0ik5ZaWzr2ob3lL-1554955528487 --from webpage source
        ticket:ST-679454-kpqNzGkqtcBHN6xRYqer-GUtc-cas-1554955650276 
    2.
        lt:LT-534828-Uz0l7bc2oHtXcGfqLCfwFODdbmmohd-1554939718865
        ticket:ST-672576-iKmLlcmR4AudBLiLucsx-GUtc-cas-1554939743273
    3.
        lt:LT-543488-BPYgPOYBmVNdKE3bmTZPMeZ7vncwRq-1554958171313
        ticket:ST-680246-VGYlUrIJp4HU0NqcFE6n-GUtc-cas-1554958264789
    '''

    s = requests.session()
    ua.update({
        "Referer": "https://auth.bupt.edu.cn/authserver/login?service=http://my.bupt.edu.cn/login.portal",
        "Origin": "https://auth.bupt.edu.cn"
    })
    # step2:用获得的cookie重新请求登录页
    req = s.get(url=url_a, params=service_params, headers=ua, cookies=cookies)
    print(req.cookies)
    with open("get1.html", "wb")as f:
        f.write(req.content)
    soup = BeautifulSoup(req.text, 'html.parser')
    lt_value = soup.find(name="input", attrs={"name": "lt"})["value"]
    yzm_element = soup.find(name="div", id="casCaptcha", attrs={"class": "userbox clearfix"})
    execution = soup.find(name="input", attrs={"name": "execution"})["value"]
    eventId_value = soup.find(name="input", attrs={"name": "_eventId"})["value"]
    rmShown_value = soup.find(name="input", attrs={"name": "rmShown"})["value"]
    # step 3: 准备登录post参数，要处理带验证码的情况
    login_params = {
        "username": username,
        "password": password,
        "lt": lt_value,  # 从service请求的网页上获得，<input type="hidden" name="lt" value="" />中的value
        "execution": execution,  # <input type="hidden" name="execution" value="">
        "_eventId": eventId_value,  # <input type="hidden" name="_eventId" value="">
        "rmShown": rmShown_value  # <input type="hidden" name="rmShown" value="">
    }
    if yzm_element is None:
        req = s.post(url=url_a, data=login_params, headers=ua, cookies=cookies)
    else:
        # todo:get验证码
        '''
        JSESSIONID=0000ZfM0IqVivxfRkq-fHkY428_:19kmg9ok9; Path=/
        Cookie: JSESSIONID=0000ZfM0IqVivxfRkq-fHkY428_:19kmg9ok9
        '''
        captcha_url = "https://auth.bupt.edu.cn/authserver/captcha.html"
        req1 = s.get(url=captcha_url, headers=ua, cookies=cookies)
        with open("captcha.png", "wb") as f:
            f.write(req1.content)
        print("需要验证码登录！")
        captcha_value = input(">>>Input captcha:")
        im = Image.open("captcha.png")
        im.show("captcha")
        while captcha_value.strip == '':
            print('Captcha cannot be empty')
            captcha_value = input(">>>Input captcha:")
        im.close()
        login_params.update({
            "captchaResponse": captcha_value
        })
        req = s.post(url=url_a, data=login_params, headers=ua, cookies=cookies)
    if req.status_code != requests.codes.found:
        print("Data post fails")
        print(login_params)
        print(req.text)
        return
    with open("post.html", "wb")as f:
        f.write(req.content)
    '''
    Set-Cookie: JSESSIONID=***; Path=/


# Set-Cookie: CASPRIVACY=""; Expires=Thu, 01 Dec 1994 16:00:00 GMT; Path=/
# Set-Cookie: CASTGC=TGT-212309-7x5xseBk96FUOH0LP6mnkthk7VAi3nXLagEPwtYRuTCWbjbm9G-J7Yz-cas-1554939743266; Path=/; HttpOnly
#
# '''
    # step 4:模拟中间跳转过程，在POST过后会有三个set-cookie，要一一获取
    ticket_params = {
        "ticket": "ticket_value"  # ticket组成：ST-6位数字-30位随机string-GUtc-cas-时间戳(ms)
    }
    # step 5：用请求（？）来的ticket参数请求portal首页

    # req = s.get(url="http://my.bupt.edu.cn/index.portal", params=ticket_params, headers=ua)
    # if req.status_code!=requests.codes.found:
    #     print("ticket is not right")
    #     return
    # with open("get2.html", "wb")as f:
    #     f.write(req.content)
    # step 6:请求选课界面，希望它成功
    # jw_param={
    #     "actionType":6
    # }
    # ua.update({
    #     "Host":"jwxt.bupt.edu.cn",
    #     "Referer":""
    # })
    # req=s.get(url="https://jwxt.bupt.edu.cn/xkAction.do",allow_redirects=False,params=jw_param,headers=ua)
    # step 7:用登录时请求的CASTGC和JSESSIONID请求登出页面，退出登录，登出时将CASPRIVACY和CASTGC置空
    # outurl="https://auth.bupt.edu.cn/authserver/logout"


def main():
    # print(len(sys.argv))
    if len(sys.argv) < 3:
        print(
            "\033[0;33m All of the username and password will not be stored and they will only be used in authentication."
            "\033[0;37m")
        print("\033[0;32m usage: python auto_fill_in.py <username> <password> <using_browser>"
              "\033[0;37m")
        return
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        if len(sys.argv) == 4:
            browser = sys.argv[3]
        else:
            browser = '--ie'
            print("\033[0;33m browser not specified,use IE for default.\033[0;37m")
    # login(username, password)
    # login2(username, password, browser=browser)
    login_new(username, password)
    # login_from_portal(username, password)


if __name__ == '__main__':
    if not os.path.exists("./temp/"):
        os.makedirs("./temp/")
    try:
        import selenium, matplotlib
    except ImportError:
        print("\033[0;31m需要安装selenium和matplotlib模块才可正常运行！\033[0;31m")
    else:
        main()
