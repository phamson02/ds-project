import argparse
import pandas as pd

def clean_ner_data(df_ner, df_link, weight_threshold):
    link_dropped = df_link[df_link['weight'] > weight_threshold]

    entities = set(link_dropped['from'].values.tolist() + link_dropped['to'].values.tolist())
    node_dropped = df_ner[df_ner['entity'].isin(entities)]
    
    return node_dropped, link_dropped

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    # Dir link to entity data
    argparser.add_argument('--input', type=str, default='data/ner.csv', help='Input file')

    # Dir link to edge data
    argparser.add_argument('--output', type=str, default='data/link.csv', help='Output file')

    # Weight threshold
    argparser.add_argument('--weight_threshold', type=int, default=1, help='Weight threshold')

    args = argparser.parse_args()

    df_ner = pd.read_csv(args.input)
    df_link = pd.read_csv(args.output)

    df_ner, df_link = clean_ner_data(df_ner, df_link, args.weight_threshold)

    df_ner.to_csv(args.input, index=False)
    df_link.to_csv(args.output, index=False)