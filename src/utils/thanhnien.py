import html


def fix_thanhnien_title(title):
    '''Fix thanhnien.vn title'''
    if "<![CDATA[" not in title:
        return title

    # Decode HTML entities
    decoded_str = html.unescape(title)

    # Remove CDATA tags
    utf8_str = decoded_str.replace("<![CDATA[", "").replace("]]>", "")

    return utf8_str

if __name__ == "__main__":
    input_str = "<![CDATA[ Hộ chiếu Logistics - &#039;ch&igrave;a kh&oacute;a&#039; tạo sức bật cho doanh nghiệp xuất khẩu? ]]>"
    print(fix_thanhnien_title(input_str))