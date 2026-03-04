import joblib
import pandas as pd

# 1. Load model đã lưu
data = joblib.load('nodeshield_rf_v26_advanced.joblib')
model = data['model']
model_features = data['features']

# 2. Tạo tập dữ liệu kiểm tra (Manual Test Cases)
# Các trường hợp này chưa từng xuất hiện trong 181 trang bạn crawl
test_samples = [
    {"url": "google-analytics.com/collect", "is_3rd_party": 1, "url_length": 150, "height": 0, "width": 0, "request_type_script": 1, "label": "ADS (Tracker)"},
    {"url": "bet88.com/banner_new.png", "is_3rd_party": 1, "url_length": 45, "height": 90, "width": 728, "request_type_image": 1, "label": "ADS (Banner)"},
    {"url": "rophim.la/player/main.js", "is_3rd_party": 0, "url_length": 30, "height": 0, "width": 0, "request_type_script": 1, "label": "SẠCH (Internal JS)"},
    {"url": "cdnjs.cloudflare.com/jquery.js", "is_3rd_party": 1, "url_length": 50, "height": 0, "width": 0, "request_type_script": 1, "label": "SẠCH (Trusted CDN)"},
    {"url": "img.bet-banner.site/gif", "is_3rd_party": 1, "url_length": 80, "height": 250, "width": 300, "request_type_image": 1, "label": "ADS (Pop-up)"}
]

# 3. Chuyển thành DataFrame và căn chỉnh cột
df_test = pd.DataFrame(test_samples)
# Đảm bảo các cột khớp hoàn toàn với model (điền 0 cho các cột thiếu)
df_input = df_test.reindex(columns=model_features, fill_value=0)

# 4. Dự đoán
predictions = model.predict(df_input)
# Thay vì dùng model.predict(), hãy dùng predict_proba
probs = model.predict_proba(df_input)[:, 1]

# Cài đặt ngưỡng chặn nhạy hơn (ví dụ 0.35)
threshold = 0.35
predictions = (probs >= threshold).astype(int)

print(f"{'Dự đoán':<10} | {'Xác suất':<10} | {'Kết quả'}")
for i, pred in enumerate(predictions):
    res = "ADS ❌" if pred == 1 else "SẠCH ✅"
    print(f"{res:<10} | {probs[i]:.4f}   | {test_samples[i]['label']}")