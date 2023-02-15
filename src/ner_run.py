import argparse
import pandas as pd
from itertools import combinations
from tqdm import tqdm
from underthesea import ner


def get_ner_data(content):
    entities = []

    for sentence in content.split('. '):
        try:
            res = ner(sentence, deep=True)
        except Exception as e:
            print(e)
            continue

        excluded_words = set()
        words = []
        for e in res:
            if e['entity'][-3:] not in ['PER', 'ORG']:
                continue
            word_ = e["word"]
            type_ = e["entity"]

            excluded_words.add(word_)
            if type_.startswith("I-"):
                if len(words) > 0:
                    w = words[-1]
                    words.pop()
                    excluded_words.add(w[0])
                    word_ = w[0] + ' ' + word_
                    words.append((word_, w[1]))
            else:
                words.append((word_, type_))
                
        for w in words:
            if (w[0] not in [e[0] for e in entities]) and (w[0] not in excluded_words) and (w[0][0].isalnum()) and (len(w[0]) > 1):
                entities.append(w)

    # TODO: implement further filtering of entities
        
    combs = list(combinations([e[0] for e in entities], 2))

    return entities, combs

def main(arg):
    df = pd.read_csv(arg.input)

    ner_list = []
    link_list = []

    for _, row in tqdm(df.iterrows(), total=df.shape[0]):
        if isinstance(row["content"], float):
            print(f'Found NaN at row {row["id"]}, {row["url"]}')
            continue
        ner, link = get_ner_data(row["content"])
        ner_list += ner
        link_list += [(fr, to, row["id"]) for fr, to in link]


    df_ner = pd.DataFrame(ner_list, columns=["entity", "type"])
    df_link = pd.DataFrame(link_list, columns=["from", "to", "article_ids"])

    # drop duplicate entities
    df_ner.drop_duplicates(subset=["entity"], inplace=True)
    df_ner['type'] = df_ner['type'].str[-3:]

    # Store the combination of 'from' and 'to' in the alphabetical order to drop duplicate links
    df_link["from_to"] = df_link.apply(lambda x: sorted([x["from"], x["to"]]), axis=1)
    df_link["from_to"] = df_link["from_to"].apply(lambda x: " ".join(x))
    df_link.drop_duplicates(subset=["from_to", "article_ids"], inplace=True)
    df_link.drop("from_to", axis=1, inplace=True)

    # transform df_link to have 4 columns (from, to, weight, links)
    df_link = df_link.groupby(["from", "to"]).agg({"article_ids": lambda x: list(x)}).reset_index()
    df_link["weight"] = df_link["article_ids"].apply(lambda x: len(x))

    df_ner.index.name = "id"
    df_ner.to_csv(arg.output + "ner.csv", index="id")
    df_link.index.name = "id"
    df_link.to_csv(arg.output + "link.csv", index="id")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract NER data')

    parser.add_argument('-i', '--input', help='Path to input csv file', default='data/articles.csv')
    parser.add_argument('-o', '--output', help='Path to output csv file', default='data/')

    args = parser.parse_args()
    main(args)
