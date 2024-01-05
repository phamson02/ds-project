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


def filter_articles_in_date_range(
    items, start_date, end_date, timezone_str="Asia/Ho_Chi_Minh"
):
    """Filter articles published within a specific date range"""
    start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    start_date = start_date.astimezone(pytz.timezone(timezone_str)).strftime("%Y-%m-%d")
    end_date = end_date.astimezone(pytz.timezone(timezone_str)).strftime("%Y-%m-%d")

    return [
        item
        for item in items
        if start_date <= parse(item["published"]).strftime("%Y-%m-%d") <= end_date
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


def scrape_rss(rss_link, category=None, start_date=None, end_date=None):
    """Scrape all articles' links from rss_link"""
    try:
        rss = feedparser.parse(rss_link)
    except Exception as e:
        logging.error(f"Error parsing RSS feed {rss_link}: {e}")
        return [], []

    with open("docs/excluded-sources.txt", "r") as f:
        excluded_sources = f.read().splitlines()

    if start_date and end_date:
        rss["items"] = filter_articles_in_date_range(rss["items"], start_date, end_date)

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
                if args.date:
                    logging.info(f"Scraping {rss_link} on {args.date}")
                    args.start_date = args.date
                    args.end_date = args.date
                elif args.start_date and args.end_date:
                    logging.info(
                        f"Scraping {rss_link} from {args.start_date} to {args.end_date}"
                    )
                else:
                    logging.info(f"Scraping all links {rss_link}")
                rss_articles, rss_err_articles = scrape_rss(
                    rss_link, category, args.start_date, args.end_date
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
    elif args.start_date and args.end_date:
        file_name = f"articles_{args.start_date}--{args.end_date}.csv"
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
    parser.add_argument(
        "--start-date", help="Start date for article scraping (YYYY-MM-DD)"
    )
    parser.add_argument("--end-date", help="End date for article scraping (YYYY-MM-DD)")
    args = parser.parse_args()

    # Start date and end date must be specified together
    if not (args.start_date and args.end_date) and (args.start_date or args.end_date):
        raise ValueError(
            "Invalid argument: Both start_date and end_date must be specified"
        )

    # If date is specified, and start_date or end_date is also specified, raise error invalid argument
    if args.date and (args.start_date or args.end_date):
        raise ValueError(
            "Invalid argument: Either filter by date or date range, not both"
        )

    main(args)
