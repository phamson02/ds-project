import argparse
import datetime
import os
import pandas as pd
import newspaper
import feedparser
from newspaper import Article
from newspaper import Config
from dateutil.parser import parse
import pytz

from utils import open_vnanet_article


USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0'

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 20

def article_content_scraper(article_link):
    '''Scrape article content from article_link'''
    article = Article(article_link, config=config)
    article.download()
    article.parse()
    return article.text

def scrape_rss(rss_link, category=None, today_only=False):
    '''Scrape all articles' link from rss_link'''
    rss = feedparser.parse(rss_link)

    print('Total articles:', len(rss['items']))

    # load all excluded sources
    with open('docs/excluded-sources.txt', 'r') as f:
        excluded_sources = f.read().splitlines()

    if today_only:
        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        today = datetime.datetime.now(tz=vietnam_tz)
        today = today.strftime('%Y-%m-%d')

        rss['items'] = [item for item in rss['items'] if parse(item['published']).strftime('%Y-%m-%d') == today]

    articles = []
    err_articles = []
    for item in rss['items']:
        # check if source is excluded
        excluded = any(source in item['link'] for source in excluded_sources)
        if not excluded:
            article = [item['link'], item['title'], parse(item['published']).strftime('%Y-%m-%d'), category]
            articles.append(article)

    for article in articles:
        # Article links from vnnet.vn need special treatment
        if 'vnanet.vn' in article[0]:
            article[0] = open_vnanet_article(article[0])

        try:
            # Try to scrape article content, if failed, use article title as content
            content = article_content_scraper(article[0]) or article[1]
            article.append(content)
        except newspaper.article.ArticleException as e:
            article.append(article[1])
            err_articles.append(article[0])
            print(article[0], e)

    return articles, err_articles

def main(args):
    # Get all file dir in docs/news-sources
    files = os.listdir('docs/news-sources')
    
    articles = []
    err_articles = []

    for file in files:
        with open(args.dir + file, 'r') as f:
            rss_links = f.readlines()
            rss_links = [rss_link.strip() for rss_link in rss_links]
            category = file.split('.')[0]

            for rss_link in rss_links:
                print('Scraping', rss_link)
                rss_articles, rss_err_articles = scrape_rss(rss_link, category, args.today)
                articles.extend(rss_articles)
                err_articles.extend(rss_err_articles)

    # Export to csv
    df = pd.DataFrame(articles, columns=['link', 'title', 'published', 'category', 'content'])

    # Remove duplicate articles
    df = df.drop_duplicates(subset=['link'])
    
    df.index.name = 'id'
    df.to_csv(args.output + 'articles.csv', index='id')

    # Export error articles to txt
    with open(args.output + 'error-articles.txt', 'w') as f:
        for err_article in err_articles:
            f.write(err_article + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape articles from rss links')

    parser.add_argument('-d', '--dir', help='Path to rss links', default='docs/news-sources/')
    parser.add_argument('-o', '--output', help='Path to output csv file', default='docs/')

    # argument to scrape articles from today only
    parser.add_argument('--today', help='Scrape articles from today only', default=False)

    args = parser.parse_args()
    main(args)
