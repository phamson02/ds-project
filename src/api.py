# Send POST request to https://mongodb-f71r.onrender.com
import argparse
import pandas as pd
import requests

head = {'accept': 'application/json', 'Content-Type': 'application/json', 'Content-Length': '2000'}

def main(args):
    url = 'https://mongodb-f71r.onrender.com/api/'
    
    if args.type == 'article':
        url += 'article'

        id_arr = []
        for chunk in pd.read_csv(args.input, chunksize=10):
            articles = chunk
            articles.drop('id', axis=1, inplace=True)
            articles_dict = articles.to_dict('records')
            r = requests.post(url, json=articles_dict)
            
            if r.status_code == 200:
                id_arr += r.json()
            else:
                print(r.status_code)
                print(r.text)
                break
            
        # update id column
        if id_arr:
            articles = pd.read_csv(args.input)
            articles['id'] = id_arr
            articles.to_csv(args.input, index=False)

    elif args.type == 'node':
        url += 'node'

        nodes = pd.read_csv(args.input)
        nodes.drop('id', axis=1, inplace=True)
        nodes.rename(columns={'entity': 'name'}, inplace=True)
        nodes_dict = nodes.to_dict('records')

        # Send POST request to https://mongodb-f71r.onrender.com and get the response
        r = requests.post(url, json=nodes_dict)
        if r.status_code == 200:
            id_arr = r.json()
            # update id column
            nodes = pd.read_csv(args.input)
            nodes['id'] = id_arr
            nodes.to_csv(args.input, index=False)
        else:
            print(r.status_code)
            print(r.text)

    elif args.type == 'edge':
        url += 'edge'

        for chunk in pd.read_csv(args.input, chunksize=20):
            edges = chunk
            edges.drop('id', axis=1, inplace=True)
            edges.rename(columns={'from': 'source', 'to': 'target', 'article_ids': 'articles', 'weight': 'size'}, inplace=True)
            edges_dict = edges.to_dict('records')
            for edge in edges_dict:
                edge['articles'] = edge['articles'][1:-1].split(',')
                edge['size'] = int(edge['size'])

            r = requests.post(url, json=edges_dict)

            print(r.status_code)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload data to Node.js server')

    parser.add_argument('--input', type=str, required=True, help='Input file')

    parser.add_argument('--type', type=str, required=True, help='Type of data to insert')

    args = parser.parse_args()
    main(args)