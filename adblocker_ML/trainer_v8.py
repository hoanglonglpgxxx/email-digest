import pandas as pd
import joblib
import re
import os
from urllib.parse import urlparse
from sklearn.ensemble import RandomForestClassifier


def extract_features_v26(url, is_ad_label=0):
    u = str(url).lower()
    p = urlparse(u)
    domain = p.netloc

    # 1. NHẬN DIỆN "NGƯỜI LẠ TỐT" (Whitelist uy tín toàn cầu)
    trusted_domains = ["wikimedia", "wikipedia", "cdnjs", "google", "gstatic", "facebook", "twitter"]
    is_trusted = 1 if any(x in domain for x in trusted_domains) else 0

    # 2. TỪ KHÓA NHẠY CẢM (Mở rộng để bắt tracker)
    keywords = r'ad|banner|bet|click|track|luxe|fun|analytics|collect|promo|789club|tx88'
    has_keyword = 1 if re.search(keywords, u) else 0

    # 3. ĐẶC TRƯNG NỘI BỘ
    is_internal = 1 if "rophim.la" in domain or not domain else 0

    return {
        "is_internal": is_internal,
        "is_trusted": is_trusted,
        "has_keyword": has_keyword,
        "url_len": len(u),
        "num_params": len(p.query.split('&')) if p.query else 0,
        "is_ad": is_ad_label
    }


def main():
    rows = []
    # Nạp 2000 mẫu sạch (Tăng độ rộng để AI không bị "cận thị")
    if os.path.exists("dataset_hybrid_2026.csv"):
        df_old = pd.read_csv("dataset_hybrid_2026.csv")
        clean = df_old[df_old['is_ad'] == 0].sample(n=min(2000, len(df_old)), random_state=42)
        for url in clean['url']:
            rows.append(extract_features_v26(url, 0))

    # Nạp tập Ads và nhân bản (Oversampling)
    for f in ["bet_ads_raw.csv", "bet_ads_raw_2.csv", "bet_ads_raw_3.csv"]:
        if os.path.exists(f):
            df_raw = pd.read_csv(f)
            for _, r in df_raw.iterrows():
                feat = extract_features_v26(r['target_url'], 1)
                rows.extend([feat] * 50)  # Nhân bản mạnh để cân bằng với 2000 mẫu sạch

    df = pd.DataFrame(rows).drop_duplicates()
    X = df.drop(columns=['is_ad'])
    y = df['is_ad']

    clf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    clf.fit(X, y)

    joblib.dump({"model": clf, "features": X.columns.tolist()}, 'model_hybrid_2026_v11.joblib')
    print("🚀 Đã hoàn thiện Model V26: Cân bằng giữa Độ chính xác và Khả năng tổng quát!")


if __name__ == "__main__":
    main()