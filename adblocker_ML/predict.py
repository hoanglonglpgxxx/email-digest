import joblib
import numpy as np
import pandas as pd


def predict_ad():
    print("Đang tải model từ file joblib...")
    try:
        model = joblib.load('ad_blocker_model.joblib')
    except FileNotFoundError:
        print("Lỗi: Không tìm thấy file model!")
        return

    # 2. Tạo dữ liệu giả lập (Vì ta không có ảnh thật ở đây)
    # Model của bạn cần đầu vào là 1558 thông số (chiều rộng, chiều cao, url...)
    # Ở đây mình tạo bừa 1 dòng dữ liệu toàn số 0 để test
    print("Đang tạo dữ liệu giả lập...")
    fake_data = np.zeros((1, 1558))

    # 3. Yêu cầu model dự đoán
    prediction = model.predict(fake_data)

    # 4. In kết quả
    print("-" * 30)
    if prediction[0] == 1:
        print("KẾT QUẢ: Đây là QUẢNG CÁO! (Block ngay)")
    else:
        print("KẾT QUẢ: Đây là nội dung an toàn.")
    print("-" * 30)


if __name__ == "__main__":
    predict_ad()