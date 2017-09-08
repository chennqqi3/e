# coding=utf-8
import requests
from lxml import html
headers={
   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
}
url='http://weixin.sogou.com/weixin?type=1&s_from=input&query=%E7%9C%9F%E5%AE%9E%E6%95%85%E4%BA%8B%E8%AE%A1%E5%88%92&ie=utf8&_sug_=n'
a=requests.get(url,headers=headers)
tree=html.fromstring(a.text)
url=tree.xpath('//p[@class="tit"]/a/@href')[0]
a=requests.get(url,headers=headers)
import re,json

inform_list=re.findall('msgList = (.*);',a.text)[0]
article_inform=json.loads(inform_list)
a= article_inform[u'list'][5]
#for a in  article_inform[u'list']:
has_multi=a['app_msg_ext_info']['multi_app_msg_item_list']
if has_multi:
    for b in has_multi:
        author=b['author']
        title=b['title']
        content_url='http://mp.weixin.qq.com'+b['content_url']
        print author+' '+title+content_url
author=a['app_msg_ext_info']['author']
title=a['app_msg_ext_info']['title']
content_url='http://mp.weixin.qq.com'+a['app_msg_ext_info']['content_url']
content_url= content_url.replace('amp;','')
print content_url
a=requests.get(content_url,headers=headers)
print a.text






