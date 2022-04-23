#encoding=utf-8
#修改自 https://github.com/youqingxiaozhua/GeneralNewsSpider
#清理上海发布每天发布的病例信息 since 3/26/2022 | 3月17日前每个病人都有地址 ｜ 3月18-25日每个病人都有区
#5号开始地址数据变成微信数据，无法获取
#卫健委官网没有放的一些日期
#3月13日 https://mp.weixin.qq.com/s/kdSUGd2xGR6Xx-HfekKUSA
#3月13日的疫情发布会是下午截止的数据 https://wsjkw.sh.gov.cn/xwfb/20220313/bdd4d48332a248b3a76b5e1ab786daf9.html
#3月17日	https://mp.weixin.qq.com/s/ZSIDH6G-IIrWUmXKpWGulg
#3月16日	https://mp.weixin.qq.com/s/J8Ib1MFCWI6vouw5Gz2MiQ
#3月18日	https://mp.weixin.qq.com/s/OFt7LzeHt8fNl6GqPpkD1g
#3月18日	https://mp.weixin.qq.com/s/xLVPnOTErTe3dmAenUyDGQ
#https://wsjkw.sh.gov.cn/yqtb/index.html

import re
import codecs
from os import listdir

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from newspaper import Article
from retrying import retry
from config import address_dir, number_dir

baseurl = ['https://posts.careerengine.us/author/5aa297b6971c5d0b53fa76b0/posts/1']
prefixurl = 'https://posts.careerengine.us/'
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36",
}

def crawl_list(baseurl):
    """
    解析列表
    """
    date_pattern = '((\d{1,2})月(\d{1,2})日)'
    address_pattern = '居住地信息'

    r = requests.get(baseurl, headers = headers)
    print(r)
    if r.status_code == 200:
        #获取列表
        print('--get list--')
        html = r.content
        soup = BeautifulSoup(html, features="lxml")
        filter_list = []
        wide_list = soup.find_all('li')
        for i in wide_list:
            dates = re.findall(date_pattern, i.text)
            if len(dates) >= 1:
                create_date = dates[0][0]
                date, month = re.findall('\d+', create_date)
                create_date = ("2022%02d%02d" % (int(date), int(month)))
                titles = i.find_all('a')
                for j in titles:
                    title = j.text
                    if len(title) != 0:
                        break
                if len(title) == 0:
                    continue
                try:
                    detail_url = i.find('a').get('href')
                except:
                    continue
                is_address = len(re.findall(address_pattern, i.text))
                filter_list.append((is_address, create_date, urljoin(prefixurl, detail_url), i.text))
        for is_address, create_date, url, title in filter_list:
            if not not_crawled(url):
                continue
            title, article = parse_notice_detail(url, title)
            if is_address:
                save(address_dir, create_date, article, url)
            else:
                save(number_dir, create_date, article, url)


@retry(stop_max_attempt_number=9, wait_random_min=5, wait_random_max=10)
def parse_notice_detail(url, title):
    """
    解析新闻正文
    :param url: 完整的详情页url
    :param title: 列表页解析到的标题
    :return: tuple: title, content
    """
    article = Article(url, language='zh')
    try:
        article.download()
        article.parse()
    except Exception as e:
        if 'failed with 404' in str(e):
            raise Page404Error
    return title.strip(), article.text

def not_crawled(url):
    #检查是否在已经抓取列表里
    pass
    return True

def save(dir, create_date, article, url):
    #抓取并保存
    filelist = listdir(dir)
    if create_date not in filelist:
        print(f'{create_date}  {url}')
        f = codecs.open(dir + '/' + create_date, mode='w', encoding='utf_8')
        f.write(article)
        f.close()

if __name__ == '__main__':
    for url in baseurl:
        print(url)
        crawl_list(url)
