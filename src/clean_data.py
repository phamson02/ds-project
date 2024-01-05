import argparse
import pandas as pd
import re


def clean_plo_text(text):
    # Remove the last line
    text = text.rsplit("\n", 1)[0]

    # Remove any 'PLO'
    text = text.replace("(PLO)-", "")

    return text


def clean_vtc_text(text):
    if "\n" not in text:
        return text

    # Remove the first line
    text = text.split("\n", 1)[1]

    # Remove the last line
    text = text.rsplit("\n", 1)[0]

    return text


def clean_laodong_text(text):
    if "\n" not in text:
        return text

    # Remove the first line
    text = text.split("\n", 1)[1]

    return text


def clean_vtv_text(text):
    if "\n" not in text:
        return text

    # Remove the first line
    text = text.split("\n", 1)[1]

    # Remove the last line
    text = text.rsplit("\n", 1)[0]

    # Remove any 'VTV.vn'
    text = text.replace("VTV.vn", "")

    return text


def clean_unnecessary_text(text):
    """Unnecessary text can be author, image source, etc."""
    # List of patterns of image source to remove
    patterns = [
        r"\(Ảnh:.*?\)",  # (Ảnh: VTV)
        r"\(Ảnh minh hoạ:.*?\)",  # (Ảnh minh hoạ: VTV)
        r"\(Ảnh minh họa:.*?\)",
        r"\(Nguồn:.*?\)",
        r"\(Nguồn ảnh:.*?\)",
        r"\(Nguồn video:.*?\)",
        r"Ảnh: [AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴA-Z\s]*\b",  # Ảnh: PHƯƠNG UYÊN
        r"Đồ họa: [AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴA-Z\s]*\b",
        r"ẢNH CHỤP MÀN HÌNH [AĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴAĂÂÁẮẤÀẰẦẢẲẨÃẴẪẠẶẬĐEÊÉẾÈỀẺỂẼỄẸỆIÍÌỈĨỊOÔƠÓỐỚÒỒỜỎỔỞÕỖỠỌỘỢUƯÚỨÙỪỦỬŨỮỤỰYÝỲỶỸỴA-Z\s]*\b",
    ]

    for pattern in patterns:
        text = re.sub(pattern, "", text)

    # Remove image source sentences, which start with "Ảnh: " or "Đồ họa: ", etc.
    sentences = text.split(". ")
    patterns = [
        r"Ảnh:.*",
        r"Đồ họa:.*",
        r"Ảnh minh hoạ:.*",
        r"Ảnh minh họa:.*",
        r"Video:.*",
        r"Nguồn:.*",
    ]
    for pattern in patterns:
        sentences = [
            sentence for sentence in sentences if not re.match(pattern, sentence)
        ]
    text = ". ".join(sentences)

    # Clean sentences with all uppercase characters (usually author)
    sentences = text.split(".")
    sentences = [sentence for sentence in sentences if not sentence.isupper()]
    text = ".".join(sentences)

    # Clean sentences with 2 or less words, excluding words inside parentheses (usually author)
    sentences = text.split(".")
    clean_sentences = []
    for sentence in sentences:
        if len(re.sub(r"\(.*?\)", "", sentence).split()) > 3:
            clean_sentences.append(sentence)

    text = ".".join(clean_sentences)

    return text


def clean_text(text):
    """Clean scraped text"""
    text = text.replace("BNEWS", " ")

    # text = text.replace("\n", " ")
    # text = text.replace("\t", " ")
    # text = text.replace("\r", " ")

    # Remove line breaks, check if the line before line break is a full stop, if not, add a full stop
    lines = text.splitlines(True)  # keep line breaks in list
    lines = [line for line in lines if line.strip()]  # remove empty lines
    for i, line in enumerate(lines):
        line = line.strip()
        if not line.endswith("."):
            line += "."
        lines[i] = line
    text = " ".join(lines)

    # Remove any words that contains "/TTXVN"
    words = text.split(" ")
    words = [word for word in words if "/TTXVN" not in word]
    text = " ".join(words)

    # Clean image source
    text = clean_unnecessary_text(text)

    # Strip leading and trailing spaces
    text = text.strip()

    return text


def main(args):
    df = pd.read_csv(args.input)

    # Clean VTV.vn text
    df.loc[df["url"].str.contains("vtv.vn"), "content"] = df.loc[
        df["url"].str.contains("vtv.vn"), "content"
    ].apply(clean_vtv_text)

    # Clean PLO text
    df.loc[df["url"].str.contains("plo.vn"), "content"] = df.loc[
        df["url"].str.contains("plo.vn"), "content"
    ].apply(clean_plo_text)

    # Clean VTC text
    df.loc[df["url"].str.contains("vtc.vn"), "content"] = df.loc[
        df["url"].str.contains("vtc.vn"), "content"
    ].apply(clean_vtc_text)

    # Clean laodong text
    df.loc[df["url"].str.contains("laodong.vn"), "content"] = df.loc[
        df["url"].str.contains("laodong.vn"), "content"
    ].apply(clean_laodong_text)

    # Clean all text
    df["content"] = df["content"].apply(clean_text)

    # Fill NaN values with title
    df["content"] = df["content"].fillna(df["title"])

    df.to_csv(args.output, index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean data")

    parser.add_argument(
        "-i",
        "--input",
        help="Path to input csv file",
        required=True,
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Path to output csv file",
        required=True,
    )

    args = parser.parse_args()
    main(args)
