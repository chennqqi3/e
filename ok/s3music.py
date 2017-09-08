# coding=utf-8
import requests
from zhihuibianc.SpiderMan import SpiderMan
import PyV8,re
import base64
from Crypto.Cipher import AES
import json
#core.js变量名称每天会改变，其他js文件也会使用到这些变量 需要更换js才能使用
url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_4153366?csrf_token="
iv='0102030405060708'
param_b='010001'
param_c='00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
param_d='0CoJUm6Qyw8W8jud'

# suiji16随机生成 这里写死 encSecKey有b,c,suiji16三个固定参数 也可以写死
# def get_js_fun():
#     ctxt = PyV8.JSContext()
#     ctxt.enter()
#     ctxt.eval("""
#             function a(a) {
#                 var d, e, b = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
#                 c = "";
#                 for (d = 0; a > d; d += 1) e = Math.random() * b.length,
#                 e = Math.floor(e),
#                 c += b.charAt(e);
#                 return c
#             }
#         """)
#     return ctxt.locals.a
# get16= get_js_fun()
#
# xx= get16(16)
# print xx
suiji16='FFFFFFFFFFFFFFFF'
encSecKey='257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text)
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text
def get_params(x):
    param_a= "{rid:\"R_SO_4_4153366\", offset:\"0\", total:\"true\", limit:\"20\", csrf_token:\"\"}"
    if not x==1:
        param_a= "{rid:\"R_SO_4_4153366\", offset:\"%s\", total:\"false\", limit:\"20\", csrf_token:\"\"}" %(str(x*20-20))
    iv = "0102030405060708"
    first_key = param_d
    second_key = suiji16
    h_encText = AES_encrypt(param_a, first_key, iv)
    h_encText = AES_encrypt(h_encText, second_key, iv)
    return h_encText
def get_content(url, params, encSecKey):
    data={
        'params':params,
        'encSecKey':encSecKey
    }
    order_nbr = '5fe6cf97-5592-11e7-be16-f45c89a63279'
    crawler = SpiderMan(order_nbr, keep_session=True)
    json_content=crawler.post(url,data=data).text
    return json_content
def get_pageno():
    params = get_params(1)
    print params
    json_text = get_content(url, params, encSecKey)
    json_dict = json.loads(json_text)
    total_count=int(json_dict['total'])
    if (total_count%20==0):
        total_page=total_count/20
    else:total_page=total_count/20+1
    return total_page
def get_comment(page):
    print page
    params = get_params(page)
    json_text = get_content(url, params, encSecKey)
    json_dict = json.loads(json_text)
    if page==1:
        print '热门评论***********************************'
        hotcomment=json_dict['hotComments']
        for one_comment in hotcomment:
            content=one_comment['content']
            user=one_comment['user']['nickname']
            print user+'：'+content
        print '热门评论***********************************'
    normalcomment=json_dict['comments']
    for one_comment in normalcomment:
        content=one_comment['content']
        user=one_comment['user']['nickname']
        print user+'：'+content

if __name__ == "__main__":

    pageno=get_pageno()
    for i in range(1,pageno+1):
        get_comment(i)








