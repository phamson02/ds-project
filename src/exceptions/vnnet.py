# Special handling of links scraped from vnnet rss feed

import urllib3


def open_vnnet_article(article_link):
    assert 'vnnet.vn' in article_link, 'Not a vnnet article'

    # https://vnanet.vnhttps://vnanet.vn/Frontend/TrackingView.aspx?IID=XXXXXX 
    # -> https://vnanet.vn/Frontend/TrackingView.aspx?IID=XXXXXX
    article_link = article_link.replace('https://vnanet.vnhttps://vnanet.vn', 'https://vnanet.vn')

    return urllib3.request.urlopen(article_link).geturl()