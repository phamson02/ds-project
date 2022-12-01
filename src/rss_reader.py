import feedparser

# Scrape all articles' link from rss_link
def scrape_rss(rss_link, category=None):
    rss = feedparser.parse(rss_link)

    # load all excluded sources
    with open('docs/excluded-sources.txt', 'r') as f:
        excluded_sources = f.read().splitlines()

    articles = []
    for item in rss['items']:
        # check if source is excluded
        excluded = any(source in item['link'] for source in excluded_sources)
        if not excluded:
            article = [item['link'], item['title'], item['published'], category]
            articles.append(article)
    return articles

if __name__ == '__main__':
    rss_link = 'https://vnexpress.net/rss/thoi-su.rss'
    category = 'Thời sự'
    articles = scrape_rss(rss_link)
    print(*articles, sep='\n')