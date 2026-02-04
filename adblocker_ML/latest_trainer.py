import pandas as pd
import numpy as np
import joblib
import re
import os
import math
from collections import Counter
from urllib.parse import urlparse


# --- 1. HÀM TOÁN HỌC ---
def calculate_entropy(text):
    if not text or not isinstance(text, str): return 0
    counter = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


# --- 2. BỘ TRÍCH XUẤT ĐẶC TRƯNG CHUẨN (KHỚP VỚI BẢNG GỐC) ---
def extract_features_unified(url, is_ad_label):
    url_str = str(url).lower()
    parsed = urlparse(url_str)

    # Tính toán các cột giống bảng 21k dòng của bạn
    path_parts = [x for x in parsed.path.split('/') if x]

    # Bóc tách kích thước (ví dụ: 1200x110)
    dim_match = re.search(r'(\d+)x(\d+)', url_str)
    width = int(dim_match.group(1)) if dim_match else 0
    height = int(dim_match.group(2)) if dim_match else 0

    # Phân loại request_type (rất quan trọng để cứu CSS/JS)
    if any(url_str.endswith(x) for x in ['.css', '.scss']):
        req_type = "style"
    elif url_str.endswith('.js'):
        req_type = "script"
    elif any(url_str.endswith(x) for x in ['.png', '.jpg', '.gif', '.webp']):
        req_type = "image"
    else:
        req_type = "other"

    return {
        "url": url_str,
        "is_internal": 1 if "rophim.la" in parsed.netloc or not parsed.netloc else 0,  # Cứu main.css
        "path_depth": len(path_parts),
        "url_length": len(url_str),
        "num_digits": sum(c.isdigit() for c in url_str),
        "num_params": len(parsed.query.split('&')) if parsed.query else 0,
        "width": width,
        "height": height,
        "aspect_ratio": round(width / height, 2) if height > 0 else 0,
        "entropy": calculate_entropy(url_str),  # Đặc trưng bổ trợ cực mạnh
        "has_ad_keyword": 1 if re.search(r'\b(ad|banner|bet|click|track|luxe|fun)\b', url_str) else 0,
        "request_type": req_type,
        "is_ad": is_ad_label  # Giữ nguyên nhãn gốc, không ép nhãn
    }


def main():
    final_rows = []

    # A. Nạp tập 21k dòng: Lấy URL và tính lại đặc trưng để đồng nhất
    if os.path.exists("dataset_hybrid_2026.csv"):
        print("-> Đang nạp và tính lại đặc trưng cho 21k dòng...")
        df_old = pd.read_csv("dataset_hybrid_2026.csv")
        # Chỉ lấy cột 'url' và 'is_ad' để tính lại
        for _, r in df_old.iterrows():
            final_rows.append(extract_features_unified(r['url'], r['is_ad']))

    # B. Nạp 3 file crawl Bet: Dùng target_url làm Ads chính
    for f in ["bet_ads_raw.csv", "bet_ads_raw_2.csv", "bet_ads_raw_3.csv"]:
        if os.path.exists(f):
            print(f"-> Đang xử lý file crawl: {f}")
            df_raw = pd.read_csv(f)
            for _, r in df_raw.iterrows():
                # Link Bet luôn là ADS (1)
                final_rows.append(extract_features_unified(r['target_url'], 1))

    df = pd.DataFrame(final_rows).drop_duplicates()

    # C. Tiền xử lý (One-hot encoding cho request_type)
    df = pd.get_dummies(df, columns=['request_type'], prefix='req')

    # Loại bỏ các cột không dùng để train (URL, Domain)
    X = df.drop(columns=['url', 'is_ad'])
    y = df['is_ad']

    # Huấn luyện Random Forest
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
    clf.fit(X, y)

    # Lưu Model và tên cột Feature
    joblib.dump({"model": clf, "features": X.columns.tolist()}, 'model_hybrid_2026.joblib')
    print("✅ Đã huấn luyện xong Model V7 đồng nhất!")


if __name__ == "__main__":
    main()