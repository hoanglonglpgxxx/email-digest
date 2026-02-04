import joblib
import pandas as pd
import math
import re
from urllib.parse import urlparse
from collections import Counter


# --- 1. HÀM TRÍCH XUẤT ĐẶC TRƯNG CHUẨN (PHẢI GIỐNG HỆT FILE TRAIN) ---
def calculate_entropy(text):
    if not text or not isinstance(text, str): return 0
    counter = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


def extract_features_final(url, target_url):
    # Ưu tiên Target URL vì chứa domain cá cược, nếu không có thì dùng URL ảnh
    url_str = str(target_url).lower() if pd.notna(target_url) and str(target_url) != "" else str(url).lower()
    parsed = urlparse(url_str)

    # CỨU TINH 1: Đặc trưng tĩnh (CSS, JS, Font thường là SẠCH)
    is_static_asset = 1 if any(url_str.endswith(ext) for ext in ['.css', '.js', '.woff', '.ttf']) else 0

    # CỨU TINH 2: Whitelist nội bộ (Nếu thuộc domain rophim.la thì ưu tiên SẠCH)
    is_internal = 1 if "rophim.la" in parsed.netloc or not parsed.netloc else 0

    # Keyword: Sử dụng Regex để tránh bắt nhầm 'uploads' hay 'assets'
    keywords = r'\b(ad|banner|bet|click|track|pop|luxe|fun|tx88|789club)\b'
    has_ad_keyword = 1 if re.search(keywords, url_str) else 0

    return {
        "is_internal": is_internal,
        "is_static_asset": is_static_asset,
        "url_length": len(url_str),
        "num_params": len(parsed.query.split('&')) if parsed.query else 0,
        "path_depth": len([x for x in parsed.path.split('/') if x]),
        "entropy": calculate_entropy(url_str),
        "has_ad_keyword": has_ad_keyword
    }


# --- 2. QUY TRÌNH KIỂM THỬ 10 CASES ---
def test_ai():
    test_cases = [
        {"url": "img.gif", "target": "https://tx88.fun/?a=123", "label": 1},
        {"url": "img.png", "target": "https://789club.luxe/?utm=1", "label": 1},
        {"url": "https://rophim.la/assets/css/main.css", "target": "", "label": 0},
        {"url": "https://rophim.la/uploads/avatar.png", "target": "", "label": 0},
        {"url": "https://www.google-analytics.com/collect", "label": 1},
        {"url": "https://bet88.com/click", "label": 1},
        {"url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js", "label": 0},
        {"url": "https://rophim.la/assets/js/player.js", "label": 0},
        {"url": "https://img.bet-banner.site/800x100.gif", "label": 1},
        {"url": "https://upload.wikimedia.org/mitosis.png", "label": 0}
    ]

    print(f"-> Đang nạp mô hình model_hybrid_2026.joblib...")
    try:
        # Nhớ đổi tên file khớp với file bạn đã lưu khi Train
        model_pkg = joblib.load('model_hybrid_2026.joblib')
        clf = model_pkg['model']
        feature_names = model_pkg['features']
    except Exception as e:
        print(f"LỖI: {e}")
        return

    results = []
    for case in test_cases:
        # Trích xuất đặc trưng V4
        feat_dict = extract_features_final(case['url'], case.get('target', ""))
        feat_df = pd.DataFrame([feat_dict])

        # Đảm bảo thứ tự cột khớp hoàn toàn với lúc Train
        for col in feature_names:
            if col not in feat_df.columns: feat_df[col] = 0

        # Dự đoán nhãn
        pred = clf.predict(feat_df[feature_names])[0]

        results.append({
            "URL": case['url'][:35] + "...",
            "Dự đoán": "ADS" if pred == 1 else "SẠCH",
            "Thực tế": "ADS" if case['label'] == 1 else "SẠCH",
            "Kết quả": "✅ ĐÚNG" if pred == case['label'] else "❌ SAI"
        })

    print("\n" + "=" * 60)
    print(pd.DataFrame(results).to_string(index=False))
    print("=" * 60)


if __name__ == "__main__":
    test_ai()