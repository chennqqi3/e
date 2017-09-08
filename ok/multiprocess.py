# coding=utf-8
import requests
from namecrawler import  Crawler
from lxml import html
import datetime
import time

def get_pagehtml(url):
    #Crawler是公司封装的代理爬虫 ，反爬虫
    crawler=Crawler.Crawler(True)
    page_html=crawler.get(url)
    if page_html.status_code!=200:
        print url+'页面返回不是200！！！！！！！！！！！！'
    else:
        page_html.encoding='utf-8'
        tree=html.fromstring(page_html.text)
        return tree
#宁夏
def ningxia_crawl(x):
    #print str(datetime.datetime.now())+' 宁夏爬虫开始'

        url='http://www.ngsh.gov.cn/Government/CompanyInfomation.aspx?page='+str(x)
        tree=get_pagehtml(url)
        the_table=tree.xpath('//table[@id="enterpriseList"]/tr')[1:]
        for one_tr in the_table:
            company_name=one_tr.xpath('td[2]/a/text()')[0]
            check_date=one_tr.xpath('td[10]/text()')[0]
            print check_date+company_name
def decorator(func):
    def wrapper():
        start=time.clock()
        func()
        stop=time.clock()
        print 'run_time:',(stop-start)
    return wrapper
#简单使用装饰器完成计算函数运行时间
@decorator
def main():
    import multiprocessing as mp
    p = mp.Pool(processes=5)
    for i in range(1, 11):
        p.map_async(ningxia_crawl, (i,))
    p.close()
    p.join()


if __name__ == "__main__":
    main()


