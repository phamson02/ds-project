from underthesea import ner

text = 'Vào ngày thứ Ba (giờ địa phương), Paris Hilton đã thông báo rằng cô và chồng Carter Reum đã cùng nhau chào đón đứa con đầu lòng – một cậu con trai – thông qua người mang thai hộ. Đăng một bức ảnh ngọt ngào trên Instagram - bức ảnh cô nắm tay đứa con mới sinh của mình, Paris viết "tình yêu thương không thể diễn tả bằng lời". Bức ảnh thông báo sinh con được Paris chia sẻ trên tài khoản Instagram. Ngôi sao 41 tuổi cũng xác nhận tin này với People. Cô nói: "Tôi luôn mơ ước được làm mẹ và tôi rất vui vì Carter và tôi đã tìm thấy nhau. Chúng tôi rất vui mừng được bắt đầu gia đình cùng nhau và trái tim của chúng tôi đang bùng nổ với tình yêu dành cho cậu con trai bé bỏng của chúng tôi". Tuy nhiên, người thừa kế giàu có của dòng họ Hilton không tiết lộ thời điểm đứa trẻ ra đời hay tên của con trai mình là gì. Paris Hilton lên kế hoạch sinh con vào năm 2023 - Paris Hilton tiết lộ cô đang chuẩn bị cho việc mang thai bằng cách thụ tinh trong ống nghiệm vào năm sau.'

res = ner(text, deep=True)

print(res)