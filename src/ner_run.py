import argparse
import pandas as pd
from itertools import combinations
from tqdm import tqdm
from underthesea import ner
import os
import uuid


def get_ner_data(content):
    """
    Extract Named Entity Recognition (NER) data from the content.
    """
    entities = []
    excluded_words = set()

    for sentence in content.split(". "):
        try:
            res = ner(sentence, deep=True)
        except Exception as e:
            print(f"Error in NER processing: {e}")
            continue

        processed_entities = process_entities(res, excluded_words)
        entities.extend(processed_entities)

    return list(set(entities))


def process_entities(res, excluded_words):
    """
    Process NER results to filter and combine entities.
    """
    words = []
    for e in res:
        if e["entity"][-3:] not in ["PER", "ORG"]:
            continue
        process_entity(e, words, excluded_words)

    return [w for w in words if is_valid_entity(w, excluded_words)]


def process_entity(e, words, excluded_words):
    """
    Process individual entity from NER results.
    """
    word_ = e["word"]
    type_ = e["entity"]

    excluded_words.add(word_)
    if type_.startswith("I-") and words:
        w = words.pop()
        excluded_words.add(w[0])
        word_ = w[0] + " " + word_
        words.append((word_, w[1]))
    else:
        words.append((word_, type_))


def is_valid_entity(entity, excluded_words):
    """
    Check if an entity is valid based on certain criteria.
    """
    return (
        (entity[0] not in excluded_words)
        and (entity[0][0].isalnum())
        and (len(entity[0]) > 1)
    )


def extract_entities_and_links(row):
    """
    Extract entities and links from a single row of the DataFrame.
    """
    if not isinstance(row["content"], str):
        print(f'Invalid content at row {row["id"]}, {row["url"]}')
        return [], []

    entities = get_ner_data(row["content"])
    entities = [(str(uuid.uuid4()), e[0], e[1]) for e in entities]
    links = [
        (str(uuid.uuid4()), fr[1], to[1], row["id"])
        for fr, to in combinations(entities, 2)
    ]

    return entities, links


def main(arg):
    """
    Main function to process the input file and output NER and link data.
    """
    df = pd.read_csv(arg.input)

    tqdm.pandas()
    results = df.progress_apply(extract_entities_and_links, axis=1)
    entity_list = [entity for result in results for entity in result[0]]
    link_list = [link for result in results for link in result[1]]

    print("Number of entities:", len(entity_list))
    print("Number of links:", len(link_list))

    df_entity = pd.DataFrame(entity_list, columns=["id", "entity", "type"])
    df_entity.drop_duplicates(subset=["entity"], inplace=True)
    df_entity["type"] = df_entity["type"].str[-3:]

    df_link = pd.DataFrame(link_list, columns=["id", "from", "to", "article_ids"])
    df_link = process_links(df_link)

    # Ensure output directory exists
    os.makedirs(arg.output, exist_ok=True)

    # Check if input file name contains filter which is the part after the last underscore
    # If yes, append the filter to the output file name
    if "_" in os.path.basename(arg.input):
        filter = os.path.basename(arg.input).split("_")[-1].split(".")[0]
        df_entity.to_csv(os.path.join(arg.output, f"entity_{filter}.csv"), index=False)
        df_link.to_csv(os.path.join(arg.output, f"link_{filter}.csv"), index=False)
    else:
        df_entity.to_csv(os.path.join(arg.output, "entity.csv"), index=False)
        df_link.to_csv(os.path.join(arg.output, "link.csv"), index=False)


def process_links(df_link):
    """
    Process the link DataFrame to remove duplicates and calculate weights.
    """
    df_link["from_to"] = df_link.apply(
        lambda x: " ".join(sorted([x["from"], x["to"]])), axis=1
    )
    df_link.drop_duplicates(subset=["from_to", "article_ids"], inplace=True)
    df_link.drop("from_to", axis=1, inplace=True)

    df_link = (
        df_link.groupby(["from", "to"])
        .agg(
            {
                "id": lambda x: x.iloc[0],
                "article_ids": lambda x: list(x),
            }
        )
        .reset_index()
    )
    df_link["weight"] = df_link["article_ids"].apply(len)
    return df_link


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract NER data")
    parser.add_argument(
        "-i", "--input", help="Path to input csv file", default="data/articles.csv"
    )
    parser.add_argument(
        "-o", "--output", help="Path to output csv file", default="data/"
    )

    args = parser.parse_args()
    main(args)
