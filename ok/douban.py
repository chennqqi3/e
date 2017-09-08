# coding=utf-8
import requests, re
from lxml import html
import os
import json


class Douban():
    def __init__(self, movie_name, username, pwd):
        self.movie_name = movie_name
        self.url = 'https://accounts.douban.com/login'
        self.get_movie_url = 'https://movie.douban.com/j/subject_suggest?'

        self.data = {
            'source': 'movie',
            'redir': 'https://movie.douban.com/',
            'form_email': username,
            'form_password': pwd,
            'login': '登陆'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTM'
                          'L, like Gecko) Chrome/60.0.3112.90 Safari/537.36'
        }
        self.mm = requests.session()

    def get_movie(self):
        self.mm.post(self.url, data=self.data, headers=self.headers)
        params = {'q': self.movie_name}
        a = self.mm.get(self.get_movie_url, params=params)
        movies = json.loads(a.text)
        movie_url = movies[0]['url']
        a = self.mm.get(movie_url, headers=self.headers)
        tree = html.fromstring(a.text)
        duanping_url = tree.xpath('//div[@class="mod-hd"][1]/h2/span[@class="pl"]/a/@href')[0]
        self.redir = duanping_url
        self.get_comment()

    def get_comment(self):
        redir_half = re.search('.*?comments', self.redir).group()
        while True:
            print self.redir
            a = self.mm.get(self.redir, headers=self.headers)
            tree = html.fromstring(a.text)

            nextpage = tree.xpath('//a[@class="next"]/@href')[0]
            comments = tree.xpath('//div[@id="comments"]/div[@class="comment-item"]')

            if len(comments) > 1:
                for one_comment in comments:
                    comment = one_comment.xpath('div[@class="comment"]/p/text()')[0].strip()\
                        .replace('\t', '').replace( '\n', '')
                    star = one_comment.xpath('div[@class="comment"]/h3/span[@class="comment-info"]/span[2]/@class')[0]
                    try:
                        star_count = re.search('\d+', str(star)).group()
                    except:
                        print '此影评没有打分：' + comment
                    else:
                        star_num = str(int(star_count) / 10)
                        print star_num + '星评论：' + comment
            else:
                break

            self.redir = redir_half + nextpage


if __name__ == '__main__':
    usrname = raw_input(u'usrname:')
    pwd = raw_input(u'password:')
    douban = Douban('战狼2', usrname, pwd)
    douban.get_movie()
