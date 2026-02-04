import pandas as pd
import joblib
from urllib.parse import urlparse


def extract_url_features(url):
    """Hàm trích xuất đặc trưng URL (Giống hệt lúc Crawl)"""
    try:
        parsed = urlparse(url)
        path = parsed.path
        return {
            "domain": parsed.netloc,
            "path_depth": path.count('/') if path else 0,
            "url_length": len(url),
            "is_https": 1 if parsed.scheme == 'https' else 0,
            "num_digits": sum(c.isdigit() for c in url),
            "num_params": len(parsed.query.split('&')) if parsed.query else 0
        }
    except:
        return None


def main():
    # 1. Load Model Hybrid
    print("1. Đang load model Hybrid...")
    try:
        # Load cái dict chứa cả model và tên cột mà ta đã lưu ở bước train
        saved_data = joblib.load('model_hybrid_2026.joblib')
        model = saved_data['model']
        trained_features = saved_data['feature_names']
        print("   -> Load thành công!")
    except FileNotFoundError:
        print("   -> LỖI: Không tìm thấy file 'model_hybrid_2026.joblib'. Hãy chạy train_hybrid.py trước.")
        return

    # 2. Tạo dữ liệu Test (Giả lập các trường hợp khó)
    # Ta nhập dữ liệu thô, code sẽ tự tính toán ra các con số
    test_cases = [
        # CASE 1: Banner Quảng Cáo Google (Link dài, nhiều số, kích thước chuẩn)
        {
            "url": "https://googleads.g.doubleclick.net/pagead/ads?client=ca-pub-123456789&slot=987654321",
            "width": 300,
            "height": 250,
            "request_type": "subdocument"  # iframe
        },
        # CASE 2: Ảnh tin tức bình thường (Link sạch, kích thước to)
        {
            "url": "https://vnexpress.net/folder/day/2026/02/03/avatar.jpg",
            "width": 800,
            "height": 600,
            "request_type": "image"
        },
        # CASE 3: Script theo dõi (Tracking Pixel - Link chứa từ khóa nhạy cảm, request là script)
        {
            "url": "https://analytics.tiktok.com/pixel/tracking.js?id=C123",
            "width": 0,
            "height": 0,
            "request_type": "script"
        },
        # CASE 4: Banner trá hình (Kích thước quảng cáo nhưng link sạch) -> Test độ thông minh
        {
            "url": "https://dantri.com.vn/images/promotions/banner-tet.png",
            "width": 728,
            "height": 90,
            "request_type": "image"
        }
    ]

    print("\n2. Đang xử lý dữ liệu test...")
    processed_rows = []

    for case in test_cases:
        # A. Tính toán URL Features
        url_feats = extract_url_features(case['url'])

        # B. Gom dữ liệu lại
        row = {
            "width": case['width'],
            "height": case['height'],
            # One-Hot Encoding thủ công cho request_type
            "req_image": 1 if case['request_type'] == "image" else 0,
            "req_script": 1 if case['request_type'] == "script" else 0,
            "req_subdocument": 1 if case['request_type'] == "subdocument" else 0,
            # Các tính năng URL
            "path_depth": url_feats['path_depth'],
            "url_length": url_feats['url_length'],
            "num_digits": url_feats['num_digits'],
            "num_params": url_feats['num_params'],
            "has_ad_keyword": 1 if ("ad" in case['url'] or "banner" in case['url'] or "pixel" in case['url']) else 0
        }
        processed_rows.append(row)

    # 3. Chuyển thành DataFrame
    df_test = pd.DataFrame(processed_rows)

    # [CỰC KỲ QUAN TRỌNG] ĐỒNG BỘ CỘT (ALIGNMENT)
    # Lúc train có thể có nhiều cột (ví dụ req_other, req_xhr...) mà lúc test không có.
    # Ta dùng lệnh reindex để ép DataFrame test phải có đúng các cột như lúc train.
    # Các cột thiếu sẽ được điền số 0.
    df_test = df_test.reindex(columns=trained_features, fill_value=0)

    # 4. Dự đoán
    print("\n3. Kết quả dự đoán:")
    predictions = model.predict(df_test)
    probs = model.predict_proba(df_test)[:, 1]

    print("-" * 80)
    print(f"{'LOẠI':<15} | {'KÍCH THƯỚC':<10} | {'ĐỘ TIN CẬY':<10} | {'URL (Rút gọn)'}")
    print("-" * 80)

    for i, pred in enumerate(predictions):
        url = test_cases[i]['url']
        short_url = url[:40] + "..." if len(url) > 40 else url
        size = f"{test_cases[i]['width']}x{test_cases[i]['height']}"
        result = "QUẢNG CÁO 🚫" if pred == 1 else "AN TOÀN ✅"
        confidence = f"{probs[i] * 100:.1f}%"

        print(f"{result:<15} | {size:<10} | {confidence:<10} | {short_url}")


if __name__ == "__main__":
    main()