import argparse
import networkx as nx
import pandas as pd


def main(args):
    G = nx.Graph()

    df_link = pd.read_csv(args.directory + "link.csv")
    df_ner = pd.read_csv(args.directory + "ner.csv")

    # Add edges and weights
    for index, row in df_link.iterrows():
        G.add_edge(row['from'], row['to'], weight=row['weight'])

    nodes = []
    eigenvector_cents = []
    ec_dict = nx.eigenvector_centrality(G, max_iter=1000, weight='weight')
    for node in G.nodes():
        nodes.append(node)
        eigenvector_cents.append(ec_dict[node])
    centrality_map = {}
    for n, c in zip(nodes, eigenvector_cents):
        centrality_map[n] = c

    df_ner['score'] = df_ner['id'].apply(lambda x: centrality_map.get(x, 0.0))

    df_ner.to_csv(args.directory + "ner.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Compute betweenness centrality score for each entity')
    parser.add_argument('-d', '--directory', help='Path to directory containing link and ner csv files',
                        default='data/')
    args = parser.parse_args()
    main(args)
