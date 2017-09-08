import requests
headers={
   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
}
url='https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzIwNzM2MjA4OA==&scene=124&#wechat_redirect'
print requests.get(url,verify=False).text