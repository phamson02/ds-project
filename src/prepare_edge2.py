import argparse

import pandas as pd


def map_article_id(x, df_articles):
    x = map(int, x[1:-1].split(','))
    return f"[{','.join(df_articles.iloc[x]['id'].values)}]"

def main(args):
    
    articles = pd.read_csv(args.input)
    df_link = pd.read_csv(args.output)

    df_link['article_ids'] = df_link['article_ids'].apply(lambda x: map_article_id(x, articles))

    df_link.to_csv(args.output, index=False)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    # Dir link to entity data
    argparser.add_argument('--input', type=str, default='docs/articles.csv', help='Input file')

    # Dir link to edge data
    argparser.add_argument('--output', type=str, default='docs/ner/link.csv', help='Output file')

    args = argparser.parse_args()

    main(args)