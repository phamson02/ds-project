import html


def fix_thanhnien_title(title):
    '''Fix thanhnien.vn title'''
    if "<![CDATA[" in title:
        title = title.replace("<![CDATA[ ", "").replace("]]>", "")

    # Decode HTML entities
    decoded_str = html.unescape(title)

    return decoded_str

if __name__ == "__main__":
    input_str = "Chiến sự ng&agrave;y 375: Ukraine khai hỏa HIMARS, Bộ trưởng Quốc ph&ograve;ng Nga c&oacute; động th&aacute;i mới ]]>"
    print(fix_thanhnien_title(input_str))