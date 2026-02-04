from latest_trainer import extract_features_unified
import joblib
import pandas as pd
from urllib.parse import urlparse


# Import hàm extract_features_unified từ file trainer...

def test_ai():
    test_cases = [
        {"url": "https://tx88.fun/?a=d843", "label": 1},
        {"url": "https://789club.luxe/?utm=1", "label": 1},
        {"url": "https://rophim.la/assets/css/main.css", "label": 0},
        {"url": "https://rophim.la/uploads/avatar.png", "label": 0},
        {"url": "https://www.google-analytics.com/collect", "label": 1},
        {"url": "https://bet88.com/click", "label": 1},
        {"url": "https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js", "label": 0},
        {"url": "https://rophim.la/assets/js/player.js", "label": 0},
        {"url": "https://img.bet-banner.site/banner_1200x110.gif", "label": 1},
        {"url": "https://upload.wikimedia.org/mitosis.png", "label": 0}
    ]

    pkg = joblib.load('model_hybrid_2026.joblib')
    clf, features = pkg['model'], pkg['features']

    results = []
    for case in test_cases:
        # Nhãn truyền vào là 0 (không quan trọng lúc test)
        f_dict = extract_features_unified(case['url'], 0)
        f_df = pd.DataFrame([f_dict]).drop(columns=['url', 'is_ad'])
        f_df = pd.get_dummies(f_df, columns=['request_type'], prefix='req')

        for col in features:
            if col not in f_df.columns: f_df[col] = 0

        pred = clf.predict(f_df[features])[0]
        results.append({
            "Dự đoán": "ADS" if pred == 1 else "SẠCH",
            "Thực tế": "ADS" if case['label'] == 1 else "SẠCH",
            "Kết quả": "✅" if pred == case['label'] else "❌",
            "URL": case['url'][:35] + "..."
        })
    print(pd.DataFrame(results).to_string(index=False))


if __name__ == "__main__":
    test_ai()