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
    entities = set()

    for sentence in content.split(". "):
        try:
            ner_results = ner(sentence, deep=True)
            entities.update(process_entities(ner_results))
        except Exception as e:
            print(f"Error in NER processing: {e}")

    return list(entities)


def process_entities(ner_results, extracted_types=["PER", "ORG"]):
    """
    Process NER results to filter, combine entities, and extract unique entities.
    """
    combined_entities = []
    current_entity = []
    current_type = None

    excluded_words = set()

    for token in ner_results:
        word, entity_type = token["word"], token["entity"]

        if entity_type[-3:] in extracted_types:
            if entity_type.startswith("B-") or current_type != entity_type[-3:]:
                finalize_current_entity(
                    combined_entities, current_entity, current_type, excluded_words
                )
                current_entity = [word]
                current_type = entity_type[-3:]
            elif entity_type.startswith("I-") and current_type == entity_type[-3:]:
                current_entity.append(word)
        else:
            # Finalize the current entity if the current token is not part of an entity
            finalize_current_entity(
                combined_entities, current_entity, current_type, excluded_words
            )

    # Finalize the last entity if present
    finalize_current_entity(
        combined_entities, current_entity, current_type, excluded_words
    )

    return [
        (entity, entity_type)
        for entity, entity_type in combined_entities
        if (entity not in excluded_words) and is_valid_entity(entity)
    ]


def finalize_current_entity(
    combined_entities, current_entity, current_type, excluded_words
):
    """
    Finalize the current entity and add it to the list of combined entities.
    """
    if current_entity:
        entity = " ".join(current_entity)
        entity_type = current_type[-3:] if current_type else None
        combined_entities.append((entity, entity_type))

        # Add subwords to the list of excluded words (e.g. "Nguyễn Văn A" -> "Nguyễn", "Văn", "A", "Nguyễn Văn", "Văn A")
        subwords = get_subwords(entity)
        excluded_words.update(subwords)

        # Clear current entity and type for the next one
        current_entity.clear()
        current_type = None


def get_subwords(name):
    words = name.split()
    subwords = []
    for i in range(len(words)):
        subwords.append(words[i])
        if i < len(words) - 1:
            subwords.append(words[i] + " " + words[i + 1])
    return subwords


def is_valid_entity(entity):
    """
    Check if an entity is valid based on certain criteria.
    """
    return (entity[0].isalnum()) and (len(entity) > 1)


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
    Process the link DataFrame to combine links between the same nodes and aggregate article IDs.
    """
    # Create a sorted combination of 'from' and 'to' to identify unique links.
    df_link["from_to"] = df_link.apply(
        lambda x: "///".join(sorted([x["from"], x["to"]])), axis=1
    )

    # Aggregate the links.
    aggregated_links = (
        df_link.groupby("from_to")
        .agg(
            {
                "id": lambda ids: ids.iloc[0],  # Preserve one ID from the group.
                "article_ids": lambda article_ids: list(
                    set(article_ids)
                ),  # Combine all article IDs.
            }
        )
        .reset_index()
    )

    # Split 'from_to' back into 'from' and 'to', and calculate the weight.
    aggregated_links[["from", "to"]] = aggregated_links["from_to"].str.split(
        "///", expand=True
    )
    aggregated_links["weight"] = aggregated_links["article_ids"].apply(len)

    # Drop the 'from_to' column as it's no longer needed.
    aggregated_links.drop("from_to", axis=1, inplace=True)

    return aggregated_links


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
