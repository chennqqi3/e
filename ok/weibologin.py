# coding=utf-8
import base64
import rsa, re, json
import urllib, requests, urllib2
import binascii
from lxml import html


class WeiBoLogin():
    def __init__(self, username, pwd, enableProxy=False):
        self.weibo_ahead = 'http://weibo.com'
        self.username = username
        self.pwd = pwd
        self.enableProxy = enableProxy

    def get_encrypted_name(self):
        username_urllike = urllib.quote(self.username)
        username_encrypted = base64.b64encode(bytes(username_urllike))
        return username_encrypted.decode('utf-8')

    def get_encrypted_pw(self, data):
        rsa_e = 65537  # 0x10001
        pw_string = str(data['servertime']) + '\t' + str(data['nonce']) + '\n' + str(self.pwd)
        key = rsa.PublicKey(int(data['pubkey'], 16), rsa_e)
        pw_encypted = rsa.encrypt(pw_string.encode('utf-8'), key)
        # self.password = ''   #安全起见清空明文密码
        passwd = binascii.b2a_hex(pw_encypted)
        return passwd

    def get_prelogin_args(self):
        json_pattern = re.compile('\((.*)\)')
        url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.prelo' \
              'ginCallBack&su=&' + self.get_encrypted_name() + '&rsakt=mod&checkpin=1&client=ssologin.js(v1.4.18)'
        try:
            request_htm = requests.get(url)
            raw_data = request_htm.text
            json_data = json_pattern.search(raw_data).group(1)
            data = json.loads(json_data)
            return data
        except Exception, e:
            print 'get pre_login wrong****'

    def create_post_data(self, raw):
        post_data = {
            "entry": "weibo",
            "gateway": "1",
            "from": "",
            "savestate": "7",
            "useticket": "1",
            "pagerefer": "http://passport.weibo.com/visitor/visitor?entry=miniblog&a=enter&"
                         "url=http%3A%2F%2Fweibo.com%2F&domain=.weibo.com&ua=php-sso_sdk_client-0.6.14",
            "vsnf": "1",
            "su": self.get_encrypted_name(),
            "service": "miniblog",
            "servertime": raw['servertime'],
            "nonce": raw['nonce'],
            "pwencode": "rsa2",
            "rsakv": raw['rsakv'],
            "sp": self.get_encrypted_pw(raw),
            "sr": "1920*1080",
            "encoding": "UTF-8",
            "prelt": "606",
            "url": "http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feed"
                   "BackUrlCallBack",
            "returntype": "META"
        }
        data = urllib.urlencode(post_data).encode('utf-8')
        return data

    def enableCookies(self, enableProxy):
        # 建立一个cookies 容器
        import cookielib
        cookiejar = cookielib.LWPCookieJar()  # 建立COOKIE
        cookie_support = urllib2.HTTPCookieProcessor(cookiejar)
        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http': 'http://122.96.59.107:843'})  # 使用代理
            opener = urllib2.build_opener(proxy_support, cookie_support, urllib2.HTTPHandler)
            print "Proxy enable"
        else:
            opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        # 自定义opener获取cookie urlopen会自动打开opener
        urllib2.install_opener(opener)

    def login(self):
        url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
        self.enableCookies(self.enableProxy)
        data = self.get_prelogin_args()
        post_data = self.create_post_data(data)
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, li'
                              'ke Gecko) Chrome/58.0.3029.110 Safari/537.36'
            }
            req = urllib2.Request(
                url=url,
                data=post_data,
                headers=headers
            )
            result = urllib2.urlopen(req)
            html = result.read()
            # print html
        except Exception, e:
            print(e)
        else:
            p = re.compile('location\.replace\(\'(.*?)\'\)')
            login_url = p.search(html).group(1)
            html_page = urllib2.urlopen(login_url).read()
            # print html_page
            # html_page=requests.get(login_url)

            p2 = re.compile('"uniqueid":"(.*?)"')
            p3 = re.compile('"userdomain":"(.*?)"')

            back_url_ids = p2.search(html_page).group(1)
            back_url_domain = p3.search(html_page).group(1)
            whole_url = 'http://weibo.com/u/' + back_url_ids + '/home' + back_url_domain
            html_page = urllib2.urlopen(whole_url).read()
            return html_page

    def deal_content(self, html_page, search_word):
        tree = html.fromstring(html_page)
        content = tree.xpath('//script')
        for one_script in content:
            script_content = one_script.xpath('text()')[0]
            # p=re.compile('WB_feed_detail')
            p = re.compile(search_word)
            if p.search(script_content):
                script_content = script_content[8:-1]
                content_json = json.loads(str(script_content))
                html_content = content_json['html']
                return html_content

    def get_content(self, html_page):
        html_content = self.deal_content(html_page, 'nameBox')
        tree = html.fromstring(html_content)
        guanzhu_url_back = tree.xpath('//ul/li[1]/a/@href')[0]
        guanzhu_url = self.weibo_ahead + guanzhu_url_back
        html_page = urllib2.urlopen(guanzhu_url).read()
        guanzhu_content = self.deal_content(html_page, 'mod_pic S_line1')
        tree = html.fromstring(guanzhu_content)
        member_box = tree.xpath('//div[@class="member_box"]/ul/li')[1]
        for one_member in member_box:
            # member_url=one_member.xpath('//p[@class="pic_box"]/a/@href')[0]
            member_url = '/u/1799718830?from=myfollow_all'
            whole_member_url = self.weibo_ahead + member_url
            html_page = urllib2.urlopen(whole_member_url).read()
            one_member_content = self.deal_content(html_page, 'WB_feed_detail')
            # 还未处理过的页面信息 需要通过xpath获取内容
            print one_member_content
            # 获取的页面内容并不是一页的全部，还需要添加参数pagebar获取全部内容可用fiddler调试


if __name__ == '__main__':
    usrname = raw_input(u'usrname:')
    pwd = raw_input(u'password:')
    weibo = WeiBoLogin(usrname, pwd)
    # weibo.login()
    page_html = weibo.login()
    weibo.get_content(page_html)
