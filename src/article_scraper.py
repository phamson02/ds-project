import argparse
import datetime
import os
import pandas as pd
import newspaper
import feedparser
from newspaper import Article, Config
from dateutil.parser import parse
import pytz
import logging
import uuid

from utils import open_vnanet_article, fix_thanhnien_title

# Setting up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:78.0) Gecko/20100101 Firefox/78.0"
)

config = Config()
config.browser_user_agent = USER_AGENT
config.request_timeout = 20


def article_content_scraper(article_link):
    """Scrape article content from article_link"""
    try:
        article = Article(article_link, config=config)
        article.download()
        article.parse()
        return article.text
    except newspaper.article.ArticleException as e:
        logging.error(f"Error scraping {article_link}: {e}")
        return None


def filter_articles_by_date(items, target_date, timezone_str="Asia/Ho_Chi_Minh"):
    """Filter articles published on a specific date"""
    target_date = datetime.datetime.strptime(target_date, "%Y-%m-%d")
    target_date = target_date.astimezone(pytz.timezone(timezone_str)).strftime(
        "%Y-%m-%d"
    )
    return [
        item
        for item in items
        if parse(item["published"]).strftime("%Y-%m-%d") == target_date
    ]


def process_article_item(item, category, excluded_sources):
    """Process a single article item from RSS feed"""
    if any(source in item["link"] for source in excluded_sources):
        return None

    article = [
        str(uuid.uuid4()),  # UUID as unique identifier
        item["link"],
        item["title"],
        parse(item["published"]).strftime("%Y-%m-%d"),
        category,
    ]

    # Special treatments for certain sources
    if "vnanet.vn" in article[1]:
        article[1] = open_vnanet_article(article[1])
    if "thanhnien.vn" in article[1]:
        article[2] = fix_thanhnien_title(article[2])

    content = article_content_scraper(article[1])
    article.append(content if content else article[2])
    return article


def scrape_rss(rss_link, category=None, filter_date=None):
    """Scrape all articles' links from rss_link"""
    try:
        rss = feedparser.parse(rss_link)
    except Exception as e:
        logging.error(f"Error parsing RSS feed {rss_link}: {e}")
        return [], []

    with open("docs/excluded-sources.txt", "r") as f:
        excluded_sources = f.read().splitlines()

    if filter_date:
        rss["items"] = filter_articles_by_date(rss["items"], filter_date)

    logging.info(f"Collected articles: {len(rss['items'])}")

    articles, err_articles = [], []
    for item in rss["items"]:
        processed_article = process_article_item(item, category, excluded_sources)
        if processed_article:
            articles.append(processed_article)
        else:
            err_articles.append(item["link"])

    return articles, err_articles


def main(args):
    files = os.listdir(args.dir)

    articles, err_articles = [], []
    for file in files:
        with open(os.path.join(args.dir, file), "r") as f:
            rss_links = [rss_link.strip() for rss_link in f.readlines()]
            category = os.path.splitext(file)[0]

            for rss_link in rss_links:
                logging.info(f"Scraping {rss_link}")
                rss_articles, rss_err_articles = scrape_rss(
                    rss_link, category, args.date
                )
                articles.extend(rss_articles)
                err_articles.extend(rss_err_articles)

    df = pd.DataFrame(
        articles, columns=["id", "url", "title", "pubDate", "category", "content"]
    )
    df = df.drop_duplicates(subset=["url"])

    if not os.path.exists(args.output):
        os.makedirs(args.output)

    if args.date:
        file_name = f"articles_{args.date}.csv"
    else:
        file_name = "articles.csv"

    df.to_csv(os.path.join(args.output, file_name), index=False)

    with open(os.path.join(args.output, "error-articles.txt"), "w") as f:
        f.writelines(err_article + "\n" for err_article in err_articles)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape articles from rss links")
    parser.add_argument(
        "-d", "--dir", help="Path to rss links", default="docs/news-sources/"
    )
    parser.add_argument(
        "-o", "--output", help="Path to output csv file", default="data/"
    )
    parser.add_argument(
        "--date", help="Scrape articles from a specific date (YYYY-MM-DD)"
    )
    args = parser.parse_args()
    main(args)
