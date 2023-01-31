import pandas as pd
import networkx as nx
from tqdm import tqdm
import matplotlib.pyplot as plt
from networkx.algorithms.community.kclique import k_clique_communities

def get_df_link_with_weight(df_link_, weight_threshold=6):
    df_link = df_link_.groupby(['from', 'to']).size().reset_index()
    df_link.rename(columns={0: 'weight'}, inplace=True)
    df_link = df_link[df_link['weight'] > weight_threshold]
    df_link.reset_index(drop=True, inplace=True)
    df_link.sort_values('weight', ascending=False).head(10)
    return df_link

def get_graph_from_link(df_link_, weight_threshold=6):
    df_link = get_df_link_with_weight(df_link_, weight_threshold=weight_threshold)
    G = nx.Graph()
    for link in tqdm(df_link.index):
        G.add_edge(df_link.iloc[link]['from'],
                   df_link.iloc[link]['to'],
                   weight=df_link.iloc[link]['weight'])
    return G

def get_graph_centralities(G):
    # Centrality
    nodes = []
    eigenvector_cents = []
    ec_dict = nx.eigenvector_centrality(G, max_iter=1000, weight='weight')
    for node in tqdm(G.nodes()):
        nodes.append(node)
        eigenvector_cents.append(ec_dict[node])
    df_centrality = pd.DataFrame(data={
        'entity': nodes,
        'centrality': eigenvector_cents
    })
    return df_centrality

def get_all_cliques(df_link, clique_size_threshold=7, weight_threshold=6):
    G = get_graph_from_link(df_link, weight_threshold=weight_threshold)
    return list(k_clique_communities(G, clique_size_threshold))

def get_clique_graph_from_link(df_link_, clique, weight_threshold=6):
    df_link = get_df_link_with_weight(df_link_, weight_threshold=weight_threshold)
    # print(clique)
    cG = nx.Graph()
    for link in tqdm(df_link.index):
        f = df_link.iloc[link]['from']
        t = df_link.iloc[link]['to']
        w = df_link.iloc[link]['weight']
        if f in clique and t in clique:
            cG.add_edge(f, t, weight=w)
    return cG

def save_graph(G, file=None, subG=None, figsize=(20, 10)):
    # Sub-graph
    clique_nodes = None
    if subG:
        clique_nodes = subG.nodes()

    # Graph
    pos = nx.kamada_kawai_layout(G)
    nodes = G.nodes()
    fig, axs = plt.subplots(1, 1, figsize=figsize)
    el = nx.draw_networkx_edges(G, pos, alpha=0.1, ax=axs)
    nl = nx.draw_networkx_nodes(G, pos, nodelist=nodes,
                                node_color='#FAA6FF', node_size=50, ax=axs)
    if subG is None:
        ll = nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    else:
        nl = nx.draw_networkx_nodes(G, pos, nodelist=clique_nodes,
                                node_color='#21B5CC', edgecolors='#000000',
                                node_size=50, ax=axs)
    if file is not None:
        fig.savefig(file)
