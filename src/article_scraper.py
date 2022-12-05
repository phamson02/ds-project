import pandas as pd
import newspaper
from newspaper import Article
from exceptions import open_vnnet_article

from rss_reader import scrape_rss

def article_content_scraper(article_link):
    article = Article(article_link)
    article.download()
    article.parse()
    return article.text

if __name__ == '__main__':
    rss_links = []
    # Read till meet '----' to stop
    with open('docs/news-sources-rss.txt', 'r') as f:
        for line in f:
            if 'STOP' in line.strip():
                break
            rss_links.append(line.strip())

    # Scrape all articles' link from rss_link
    articles = []
    err_articles = []
    for rss_link in rss_links:
        print('Scraping', rss_link)
        articles += scrape_rss(rss_link)
        for article in articles:
            if 'vnnet.vn' in article[0]:
                article[0] = open_vnnet_article(article[0])

            try:
                article.append(article_content_scraper(article[0]))
            except newspaper.article.ArticleException:
                article.append('')
                err_articles.append(article[0])
        
    # Export to csv
    df = pd.DataFrame(articles, columns=['link', 'title', 'published', 'category', 'content'])
    df.to_csv('docs/articles.csv', index=False)

    # Export error articles to txt
    with open('docs/error-articles.txt', 'w') as f:
        for err_article in err_articles:
            f.write(err_article + '\n')