import feedparser

# Scrape all articles' link from rss_link
def scrape_rss(rss_link):
    rss = feedparser.parse(rss_link)
    articles = []
    for item in rss['items']:
        article = [item['link'], item['title'], item['published']]
        articles.append(article)
    return articles

if __name__ == '__main__':
    rss_link = 'https://vnexpress.net/rss/thoi-su.rss'
    articles = scrape_rss(rss_link)
    print(*articles, sep='\n')