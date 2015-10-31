# coding=utf-8
import urllib
import urllib2
import cookielib
from time import sleep

from lxml import html


# 阅读的篇数
_count = 3
# 用户名和密码
_username_and_password = {"your username1": "your password1",
                          "your username2": "your username2", }


def auto(username, password, count):
    # 登录的主页面
    login_url = 'http://www.shanbay.com/accounts/login/'
    # 获取新闻列表的页面
    news_list_url = 'http://www.shanbay.com/read/news/?page=1'
    # 服务器记录文章阅读开始的标志
    mark_url = "http://www.shanbay.com/api/v1/read/article/{}"
    # 完成阅读链接
    raw_finish_url = 'http://www.shanbay.com/api/v1/read/article/user/{}/'
    # 打卡的链接
    checkin_url = "http://www.shanbay.com/api/v1/checkin/?for_web=true"
    # 新闻链接的xpath
    news_xpath = "//div[@class='title']/a/@href"
    # 设置一个cookie处理器，它负责从服务器下载cookie到本地，并且在发送请求时带上本地的cookie
    cj = cookielib.LWPCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
    # 设置全局有效的cookie记录器
    urllib2.install_opener(opener)

    # 打开登录主页面（他的目的是从页面下载cookie，这样我们在再送post数据时就有cookie了，否则发送不成功）
    urllib2.urlopen(login_url)

    # 构造header，这两项是从抓到的包里分析得出的。
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:14.0) Gecko/20100101 Firefox/14.0.1',
               'Upgrade-Insecure-Requests': '1'}

    csrftoken = ""
    for ck in cj:
        if ck.name == 'csrftoken':
            csrftoken = ck.value

    # 构造Post数据，他也是从抓大的包里分析得出的。
    post_data = {'username': username,
                 'password': password,
                 'csrfmiddlewaretoken': csrftoken,
                 'token': ''}

    # 需要给Post数据编码
    post_data = urllib.urlencode(post_data)

    # 通过urllib2提供的request方法来向指定Url发送我们构造的数据，并完成登录过程
    request = urllib2.Request(login_url, post_data, headers)
    urllib2.urlopen(request)

    #
    dom = html.parse(urllib2.urlopen(news_list_url))
    raw_news_url = dom.xpath(news_xpath)

    for i in range(len(raw_news_url)):
        postfix = raw_news_url[i]
        if i >= count:
            request = urllib2.Request(checkin_url, None, headers)
            request.get_method = lambda: 'POST'
            response = urllib2.urlopen(request)
            print response.read()
            break
        article_id = postfix.split('/')[-2]
        news_url = mark_url.format(article_id)
        finish_url = raw_finish_url.format(article_id)
        urllib2.urlopen(news_url)
        post_data2 = {'operation': 'finish',
                      'used_time': '923'}
        post_data2 = urllib.urlencode(post_data2)
        request = urllib2.Request(finish_url, post_data2, headers)
        request.get_method = lambda: 'PUT'
        response = urllib2.urlopen(request)
        text = response.read()
        print text
        sleep(1)


for (k, v) in _username_and_password.items():
    print k + ":"
    auto(k, v, _count)

