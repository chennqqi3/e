# coding=utf-8
import requests
import re, time
from lxml import html


class Kanzhun(object):
    def __init__(self, username, pwd, company_name, city=False):
        self.city = city
        self.username = username
        self.pwd = pwd
        self.company_name = company_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML'
                          ', like Gecko) Chrome/60.0.3112.90 Safari/537.36'
        }
        self.mm = requests.session()
        self.main_url = 'http://www.kanzhun.com/'
        self.url = 'http://www.kanzhun.com/login.json'
        self.get_randomkey_url = 'http://www.kanzhun.com/login/?ka=head-signin'

    def city_code(self, city):
        city_list = {
            'shanghai': '1',
            'beijing': '7',
            'shenzhen': '49',
            'guangzhou': '34'
        }
        return city_list[city]

    def get_tree(self, url, is_post=False, params=None):
        if is_post:
            a = self.mm.post(url, headers=self.headers, data=params)
        else:
            a = self.mm.get(url, headers=self.headers)
            if a.status_code != 200:
                print url + ' status=' + str(a.status_code)
            tree = html.fromstring(a.text)
            # print a.text
            return tree

    def get_comments(self, tree):
        all_comments = tree.xpath(
            '//section[@class="f_l_con"]/section[contains(@class,"public_item review_item wrap_style")]')
        for one_comment in all_comments:
            title = one_comment.xpath('article')[0]
            comment = title.xpath('string(.)')
            print self.replace_word(comment)
        next_page = tree.xpath('//div[@class="co_pager_box"]/a[last()]')[0]
        if next_page.xpath('@class')[0] == 'next':
            href = next_page.xpath('@href')[0]
            dianping_url = self.fit_url(2, param=href)
            tree = self.get_tree(dianping_url)
            self.get_comments(tree)

    def fit_url(self, type, param=None):
        if type == 1:
            url = 'http://www.kanzhun.com/companyl/search/?q=' + self.company_name + '&stype='
        elif type == 2:
            url = 'http://www.kanzhun.com' + param
        elif type == 3:
            if self.city:
                url = 'http://www.kanzhun.com/gsrPage.json?companyId=' + self.company_id + '&companyName=' \
                      + self.company_name + '&pageNum=' + str(param) + '&cityCode=' + self.city_code(self.city) +\
                      '&sortMethod=1&employeeStatus=0'
            else:
                url = 'http://www.kanzhun.com/gsrPage.json?companyId=' + self.company_id +\
                      '&companyName=' + self.company_name + '&pageNum=' + str(param) + \
                      '&cityCode=&sortMethod=1&employeeStatus=0'
        return url

    def replace_word(self, word):
        return word.replace('\t', '').replace(' ', '').replace('...查看全文', '')

    def main(self):
        random_key_page = self.mm.get(self.get_randomkey_url, headers=self.headers)
        randomk = re.findall('\/captcha\/\?randomKey=(.*?)"', str(random_key_page.text), re.S)[0]
        data = {
            'randomKey': randomk,
            'account': self.username,
            'password': self.pwd,
            'redirect': self.main_url
        }
        self.get_tree(self.url, is_post=True, params=data)
        url = self.fit_url(1)
        tree = self.get_tree(url)
        if tree.xpath('//div[@class="wrap_style search-noresult"]'):
            print '未找到该公司信息'
        else:
            url_back = tree.xpath('//ul[@class="company_result "]/li[1]/a/@href')[0]
            self.company_id = re.search('\d+', url_back).group()
            company_page_url = self.fit_url(2, param=url_back)
            tree = self.get_tree(company_page_url)

            average_money = tree.xpath('//div[@class="profile"][last()]/dl/dt/em/text()')[0].strip()
            print '平均工资为：' + average_money
            dianping_url_back = tree.xpath('//div[@class="tab_ul"]/ul/li[3]/a/@href')[0]

            if self.city:
                city_code = 'c' + self.city_code(self.city) + '.'
                dianping_url = 'http://www.kanzhun.com' + dianping_url_back.replace(u'.', city_code)
            else:
                dianping_url = self.fit_url(2, param=dianping_url_back)
            tree = self.get_tree(dianping_url)
            if not tree.xpath('//section[@class="noresult_review clearfix"]'):
                self.get_comments(tree)


if __name__ == '__main__':
    # 看准网需要用户对自己工作过的公司进行点评才可看到他人点评
    username = raw_input(u'username:')
    pwd = raw_input(u'password:')
    company_name = '阿里巴巴'
    # 只看在上海工作的人的点评
    kanzhun = Kanzhun(username, pwd, company_name, city='shanghai')
    try:
        kanzhun.main()
    except:
        import traceback

        print traceback.format_exc()
