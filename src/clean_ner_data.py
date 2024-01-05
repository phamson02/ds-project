import argparse
import pandas as pd


def clean_ner_data(df_entity, df_link, weight_threshold):
    link_dropped = df_link[df_link["weight"] > weight_threshold]

    entities = set(
        link_dropped["from"].values.tolist() + link_dropped["to"].values.tolist()
    )
    node_dropped = df_entity[df_entity["entity"].isin(entities)]

    return node_dropped, link_dropped


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    # Dir link to entity data
    argparser.add_argument(
        "--entity",
        type=str,
        required=True,
        help="Dir link to entity data",
    )

    # Dir link to link data
    argparser.add_argument(
        "--link",
        type=str,
        required=True,
        help="Dir link to link data",
    )

    # Weight threshold
    argparser.add_argument(
        "--weight_threshold", type=int, default=1, help="Weight threshold"
    )

    # Dir link to output entity data
    argparser.add_argument(
        "--entity_output",
        type=str,
        required=True,
        help="Dir link to output entity data",
    )

    # Dir link to output link data
    argparser.add_argument(
        "--link_output",
        type=str,
        required=True,
        help="Dir link to output link data",
    )

    args = argparser.parse_args()

    df_entity = pd.read_csv(args.entity)
    df_link = pd.read_csv(args.link)

    df_entity, df_link = clean_ner_data(df_entity, df_link, args.weight_threshold)

    # Save to csv
    df_entity.to_csv(args.entity_output, index=False)
    df_link.to_csv(args.link_output, index=False)
