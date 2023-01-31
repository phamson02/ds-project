import pandas as pd
import networkx as nx
from tqdm import tqdm
import matplotlib.pyplot as plt
from networkx.algorithms.community.kclique import k_clique_communities

WEIGHT_THRESHOLD=6
CLIQUE_SIZE_THRESHOLD=7

def get_link_with_weight(df_link_):
    df_link = df_link_.groupby(['from', 'to']).size().reset_index()
    df_link.rename(columns={0: 'weight'}, inplace=True)
    df_link = df_link[df_link['weight'] > WEIGHT_THRESHOLD]
    df_link.reset_index(drop=True, inplace=True)
    df_link.sort_values('weight', ascending=False).head(10)
    return df_link

def get_graph_from_link(df_wlink):
    G = nx.Graph()
    for link in tqdm(df_wlink.index):
        G.add_edge(df_wlink.iloc[link]['from'],
                   df_wlink.iloc[link]['to'],
                   weight=df_wlink.iloc[link]['weight'])
    return G

def get_graph_centralities(G):
    # Centrality
    nodes = []
    eigenvector_cents = []
    ec_dict = nx.eigenvector_centrality(G, max_iter=1000, weight='weight')
    for node in tqdm(G.nodes()):
        nodes.append(node)
        eigenvector_cents.append(ec_dict[node])
    centrality_map = {}
    for n, c in zip(nodes, eigenvector_cents):
        centrality_map[n] = c
    return centrality_map

def get_all_cliques(df_wlink):
    G = get_graph_from_link(df_wlink)
    return list(k_clique_communities(G, CLIQUE_SIZE_THRESHOLD))

def get_clique_graph_from_link(df_wlink, clique):
    # print(clique)
    cG = nx.Graph()
    for link in tqdm(df_wlink.index):
        f = df_wlink.iloc[link]['from']
        t = df_wlink.iloc[link]['to']
        w = df_wlink.iloc[link]['weight']
        if f in clique and t in clique:
            cG.add_edge(f, t, weight=w)
    return cG

def main(args):
    df_link = pd.read_csv(args.directory + "link.csv", index_col="id")
    df_wlink = get_link_with_weight(df_link)
    cliques = get_all_cliques(df_wlink)
    cluster_map = {}
    for i in range(len(cliques)):
        for n in cliques[i]:
            cluster_map[n] = i
    print(cluster_map)
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Find and output clique')
    parser.add_argument('-d', '--directory', help='Path to directory containing link and ner csv files',
                        default='docs/ner/')
    args = parser.parse_args()
    main(args)
