import argparse
from os import mkdir
import requests


def main(args):
    '''Get csv file from Node.js server'''

    url = 'http://localhost:3001/api'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36'}

    print('Getting data from server...')

    node_response = requests.get(f'{url}/csv/node', headers=headers)
    edge_response = requests.get(f'{url}/csv/edge', headers=headers)

    if node_response.status_code != 200 or edge_response.status_code != 200:
        raise Exception('Error in response')
    else:
        print('Response OK')

    # If args.output does not exist, create it
    try:
        mkdir(args.output)
    except FileExistsError:
        pass

    with open(f'{args.output}/ner.csv', 'w') as node_file:
        node_file.write(node_response.text)

    with open(f'{args.output}/link.csv', 'w') as edge_file:
        edge_file.write(edge_response.text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get data from Node.js server')
    parser.add_argument('--output', type=str, help='Output folder', required=True)

    args = parser.parse_args()
    main(args)