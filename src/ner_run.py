from underthesea import ner
import pandas as pd

# text = 'Vào ngày thứ Ba (giờ địa phương), Paris Hilton đã thông báo rằng cô và chồng Carter Reum đã cùng nhau chào đón đứa con đầu lòng – một cậu con trai – thông qua người mang thai hộ. Đăng một bức ảnh ngọt ngào trên Instagram - bức ảnh cô nắm tay đứa con mới sinh của mình, Paris viết "tình yêu thương không thể diễn tả bằng lời". Bức ảnh thông báo sinh con được Paris chia sẻ trên tài khoản Instagram. Ngôi sao 41 tuổi cũng xác nhận tin này với People. Cô nói: "Tôi luôn mơ ước được làm mẹ và tôi rất vui vì Carter và tôi đã tìm thấy nhau. Chúng tôi rất vui mừng được bắt đầu gia đình cùng nhau và trái tim của chúng tôi đang bùng nổ với tình yêu dành cho cậu con trai bé bỏng của chúng tôi". Tuy nhiên, người thừa kế giàu có của dòng họ Hilton không tiết lộ thời điểm đứa trẻ ra đời hay tên của con trai mình là gì. Paris Hilton lên kế hoạch sinh con vào năm 2023 - Paris Hilton tiết lộ cô đang chuẩn bị cho việc mang thai bằng cách thụ tinh trong ống nghiệm vào năm sau.'

# res = ner(text, deep=True)

# print(res)

def get_ner_data(content, ner_path, link_path):
    entities = {}
    for line in content.split("\n\n"):
        res = ner(line, deep=True)
        excluded_words = set()
        words = []
        for e in res:
            word_ = e["word"]
            type_ = e["entity"]
            if type_.startswith("I-"):
                # words.append((word_, type_))
                if len(words) > 0:
                    w = words[-1]
                    words.pop()
                    excluded_words.add(w[0])
                    excluded_words.add(word_)
                    word_ = w[0] + ' ' + word_
                    words.append((word_, w[1]))
            else:
                words.append((word_, type_))
        for w in words:
            if w[0] not in entities and w[0] not in excluded_words:
                entities[w[0]] = w[1]
        
    df_ner = pd.DataFrame(data={
        "entity": [e[0] for e in entities.items()],
        "type": [e[1] for e in entities.items()]
    })
    df_ner = df_ner.sort_values("entity")
    combs = list(combinations(df_ner["entity"], 2))
    df_link = pd.DataFrame(data=combs, columns=["from", "to"])

    df_ner.to_csv(ner_path, index=False)
    df_link.to_csv(link_path, index=False)
