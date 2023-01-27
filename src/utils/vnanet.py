# Special handling of links scraped from vnnet rss feed

import urllib.request


def open_vnanet_article(article_link):
    assert 'vnanet.vn' in article_link, 'Not a vnanet article'

    # https://vnanet.vnhttps://vnanet.vn/Frontend/TrackingView.aspx?IID=XXXXXX 
    # -> https://vnanet.vn/Frontend/TrackingView.aspx?IID=XXXXXX
    article_link = article_link.replace('https://vnanet.vnhttps://vnanet.vn', 'https://vnanet.vn')

    return urllib.request.urlopen(article_link).geturl()

if __name__ == '__main__':
    article_link = 'https://vnanet.vnhttps://vnanet.vn/Frontend/TrackingView.aspx?IID=6558139'
    print(open_vnanet_article(article_link))