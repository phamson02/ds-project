import argparse
import time
import pandas as pd
import requests


def main(args):
    url = 'https://lionfish-app-pnbyg.ondigitalocean.app/api/'
    
    if args.type == 'article':
        url += 'article'

        id_arr = []
        for chunk in pd.read_csv(args.input, chunksize=100):
            articles = chunk
            articles.drop('id', axis=1, inplace=True)
            articles.drop('content', axis=1, inplace=True)
            articles_dict = articles.to_dict('records')
            r = requests.post(url, json=articles_dict)
            
            if r.status_code == 200:
                id_arr += r.json()
            else:
                print(r.status_code)
                print(r.text)

                cnt_tries = 0
                while r.status_code != 200 and cnt_tries < 3:
                    time.sleep(5)
                    r = requests.post(url, json=articles_dict)
                    if r.status_code == 200:
                        id_arr += r.json()
                        break
            
        # update id column
        if id_arr:
            articles = pd.read_csv(args.input)
            articles['id'] = id_arr
            articles.to_csv(args.input, index=False)

    elif args.type == 'node':
        url += 'node'

        id_arr = []
        for chunk in pd.read_csv(args.input, chunksize=300):
            nodes = chunk
            nodes.drop('id', axis=1, inplace=True)
            nodes.rename(columns={'entity': 'name'}, inplace=True)
            nodes_dict = nodes.to_dict('records')

            r = requests.post(url, json=nodes_dict)

            print(r.status_code)
            if r.status_code == 200:
                id_arr += r.json()
            else:
                print(r.text)

                cnt_tries = 0
                while r.status_code != 200 and cnt_tries < 3:
                    time.sleep(5)
                    r = requests.post(url, json=nodes_dict)
                    if r.status_code == 200:
                        id_arr += r.json()
                        break

        if id_arr:
            nodes = pd.read_csv(args.input)
            nodes['id'] = id_arr
            nodes.to_csv(args.input, index=False)

    elif args.type == 'edge':
        url += 'edge'

        for chunk in pd.read_csv(args.input, chunksize=20):
            edges = chunk
            edges.drop('id', axis=1, inplace=True)
            edges.rename(columns={'from': 'source', 'to': 'target', 'article_ids': 'articles', 'weight': 'size'}, inplace=True)
            edges_dict = edges.to_dict('records')
            for edge in edges_dict:
                edge['articles'] = eval(edge['articles'])
                edge['size'] = int(edge['size'])

            r = requests.post(url, json=edges_dict)

            print(r.status_code)
            if r.status_code != 200:

                cnt_tries = 0
                while r.status_code != 200 and cnt_tries < 3:
                    
                    time.sleep(5)
                    r = requests.post(url, json=edges_dict)
                    if r.status_code == 200:
                        break


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Upload data to Node.js server')

    parser.add_argument('--input', type=str, required=True, help='Input file')

    parser.add_argument('--type', type=str, required=True, help='Type of data to insert')

    args = parser.parse_args()
    main(args)