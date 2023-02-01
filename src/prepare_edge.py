import argparse

import pandas as pd


def main(args):
    
    df_ner = pd.read_csv(args.input)
    df_link = pd.read_csv(args.output)

    # Transfrom from and to to id in ner
    df_link['from'] = df_link['from'].apply(lambda x: df_ner[df_ner['entity'] == x]['id'].values[0])
    df_link['to'] = df_link['to'].apply(lambda x: df_ner[df_ner['entity'] == x]['id'].values[0])

    df_link.to_csv(args.output, index=False)

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()

    # Dir link to entity data
    argparser.add_argument('--input', type=str, default='docs/ner/ner.csv', help='Input file')

    # Dir link to edge data
    argparser.add_argument('--output', type=str, default='docs/ner/link.csv', help='Output file')

    args = argparser.parse_args()

    main(args)