import numpy as np
import joblib
import math
import re
import os
import pandas as pd
import joblib
import re
from urllib.parse import urlparse
from collections import Counter
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report


# --- 1. HÀM TRÍCH XUẤT ĐẶC TRƯNG V3 ---
def calculate_entropy(text):
    if not text or not isinstance(text, str): return 0
    counter = Counter(text)
    length = len(text)
    # Công thức Shannon Entropy
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


def extract_features_final(url, is_ad_label=0):
    url_str = str(url).lower()
    parsed = urlparse(url_str)

    # Đặc trưng 1: Loại file (Rất quan trọng để cứu CSS/JS)
    is_static_asset = 1 if any(url_str.endswith(ext) for ext in ['.css', '.js', '.woff', '.ttf']) else 0

    # Đặc trưng 2: Domain uy tín (Whitelisting nội bộ)
    is_internal = 1 if "rophim.la" in parsed.netloc or not parsed.netloc else 0

    # Đặc trưng 3: Keyword (Regex chặt chẽ hơn)
    keywords = r'\b(ad|banner|bet|click|track|pop|luxe|fun|tx88|789club)\b'
    has_ad_keyword = 1 if re.search(keywords, url_str) else 0

    return {
        "is_internal": is_internal,
        "is_static_asset": is_static_asset,  # Đặc trưng mới cứu CSS
        "url_length": len(url_str),
        "num_params": len(parsed.query.split('&')) if parsed.query else 0,
        "path_depth": len([x for x in parsed.path.split('/') if x]),
        "has_ad_keyword": has_ad_keyword,
        "is_ad": is_ad_label
    }


def main():
    final_rows = []

    # Đọc dataset to nhất (Lấy URL và nhãn gốc)
    if os.path.exists("dataset_hybrid_2026.csv"):
        df_old = pd.read_csv("dataset_hybrid_2026.csv")
        for _, row in df_old.iterrows():
            # Chỉ lấy URL để tính lại đặc trưng
            final_rows.append(extract_features_final(row['url'], row['is_ad']))

    # Đọc các file crawl Bet của mitsne
    for f in ["bet_ads_raw.csv", "bet_ads_raw_2.csv", "bet_ads_raw_3.csv"]:
        if os.path.exists(f):
            df_raw = pd.read_csv(f)
            for _, row in df_raw.iterrows():
                # Ưu tiên target_url vì nó chứa domain Bet
                target = row['target_url'] if pd.notna(row['target_url']) else row['url']
                final_rows.append(extract_features_final(target, 1))

    df = pd.DataFrame(final_rows).drop_duplicates()

    # Huấn luyện Random Forest
    X = df.drop(columns=['is_ad'])
    y = df['is_ad']

    clf = RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
    clf.fit(X, y)

    # Lưu Model
    joblib.dump({"model": clf, "features": X.columns.tolist()}, 'model_hybrid_2026.joblib')
    print("✅ Đã huấn luyện xong Model với đặc trưng đồng nhất!")


if __name__ == "__main__":
    main()