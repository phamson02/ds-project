import argparse
import pandas as pd

def clean_plo_text(text):
    # Remove the last line
    text = text.rsplit('\n', 1)[0]

    # Remove any 'PLO'
    text = text.replace('(PLO)-', '')

    return text

def clean_vtc_text(text):
    if '\n' not in text:
        return text

    # Remove the first line
    text = text.split('\n', 1)[1]

    # Remove the last line
    text = text.rsplit('\n', 1)[0]

    return text

def clean_laodong_text(text):
    if '\n' not in text:
        return text

    # Remove the first line
    text = text.split('\n', 1)[1]

    return text

def clean_vtv_text(text):
    if '\n' not in text:
        return text

    # Remove the first line
    text = text.split('\n', 1)[1]

    # Remove the last line
    text = text.rsplit('\n', 1)[0]

    # Remove any 'VTV.vn'
    text = text.replace('VTV.vn', '')

    return text

def clean_text(text):
    '''Clean scraped text'''
    text = text.replace('BNEWS', ' ')

    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    text = text.replace('\r', ' ')

    # Clean multiple spaces
    text = ' '.join(text.split())

    return text

def main(args):
    df = pd.read_csv(args.input)
    
    # Clean VTV.vn text
    df.loc[df['url'].str.contains('vtv.vn'), 'content'] = df.loc[df['url'].str.contains('vtv.vn'), 'content'].apply(clean_vtv_text)

    # Clean PLO text
    df.loc[df['url'].str.contains('plo.vn'), 'content'] = df.loc[df['url'].str.contains('plo.vn'), 'content'].apply(clean_plo_text)

    # Clean VTC text
    df.loc[df['url'].str.contains('vtc.vn'), 'content'] = df.loc[df['url'].str.contains('vtc.vn'), 'content'].apply(clean_vtc_text)

    # Clean laodong text
    df.loc[df['url'].str.contains('laodong.vn'), 'content'] = df.loc[df['url'].str.contains('laodong.vn'), 'content'].apply(clean_laodong_text)

    # Clean text
    df['content'] = df['content'].apply(clean_text)

    if not args.output:
        args.output = args.input      
    df.to_csv(args.output, index=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Clean data')

    parser.add_argument('-i', '--input', help='Path to input csv file', default='data/articles.csv')
    
    # if no output path is specified, then the changes will be saved to the input file
    parser.add_argument('-o', '--output', help='Path to output csv file')    

    args = parser.parse_args()
    main(args)