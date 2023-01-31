import random
import pandas as pd
from src.find_clique import *
# Xử lý node.csv
data_link1 = pd.read_csv('ner.csv',encoding ='utf-8')
data_link1.head()
# remove the first 2 character  of the column 'type'
data_link1['type'] = data_link1['type'].str[2:]
# # change the column 'type' to 'tag'
data_link1.rename(columns={'type':'tag'}, inplace=True)
# change the column 'id' to 'key'
data_link1.rename(columns={'id':'key'}, inplace=True)
# change the column 'text' to 'label'
data_link1.rename(columns={'entity':'label'}, inplace=True)
# turn the column 'key' into columns 'label'
data_link1['key'] = data_link1['label']
# Create a columns 'cluster' and and 'size'
df_link = pd.read_csv("link.csv", index_col="id")
df_wlink = get_link_with_weight(df_link)
del df_link
cliques = get_all_cliques(df_wlink)
cluster_map = {}
centrality_map = {}
for i in range(len(cliques)):
    G = get_clique_graph_from_link(df_wlink, cliques[i])
    clique_centrality_map = get_graph_centralities(G)
    for n in cliques[i]:
        cluster_map[n] = i
    for key, value in clique_centrality_map.items():
        centrality_map[key] = value
data_link1['cluster'] = data_link1['key'].apply(lambda x: cluster_map.get(x, -1))
data_link1['size'] = data_link1['key'].apply(lambda x: centrality_map.get(x, -1))
# Create a columns 'x' and set the value to math.random(int)
data_link1['x'] = data_link1['key'].apply(lambda x: random.randint(0, 100))
data_link1['y'] = data_link1['key'].apply(lambda x: random.randint(0, 100))
nodes = data_link1.to_dict('records')

# Xử lý link.csv
data_link = pd.read_csv('link.csv',encoding ='utf-8')
# retieve 2 columns from and to in data_link
data_link = data_link[['from','to']]
# get the list of nodes
edges =  data_link.values.tolist()

import pandas as pd
import json 
# write json have the following structure
def write_json(data,data1,filename):
    with open(filename, 'w',encoding='utf-8') as f:
        json.dump({'nodes':data,"edges":data1,"clusters":[{ "key": "0", "color": "#6c3e81", "clusterLabel": "All nodes" }],"tags":[{ "key": "ORG", "image": "organization.svg" },{ "key": "PER", "image": "person.svg" },{ "key": "LOC", "image": "unknown.svg" }]}, f,indent=4,ensure_ascii=False)
write_json(nodes,edges, 'graph.json')
