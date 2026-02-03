import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix


def main():
    # 1. LOAD DỮ LIỆU
    print("1. Đang đọc dữ liệu 'dataset_hybrid_2026.csv'...")
    try:
        df = pd.read_csv("dataset_hybrid_2026.csv")
    except FileNotFoundError:
        print("LỖI: Không tìm thấy file csv. Hãy chạy crawler trước!")
        return

    print(f"   -> Tổng số dòng: {len(df)}")

    # 2. XỬ LÝ DỮ LIỆU (PREPROCESSING)
    print("2. Đang xử lý dữ liệu...")

    # A. Xử lý cột phân loại (Request Type)
    # Máy học không hiểu "image", "script". Ta phải tách thành các cột 0/1 (One-Hot Encoding)
    # Ví dụ: request_type='script' -> req_script=1, req_image=0
    df = pd.get_dummies(df, columns=['request_type'], prefix='req')

    # B. Chọn các cột đặc trưng (Features)
    # Ta loại bỏ các cột không dùng để train:
    # - 'is_ad': Đây là đáp án (Label)
    # - 'url', 'domain': Đây là text thô (Ta chưa dùng NLP ở bước này)
    # - 'width', 'height': Giữ lại
    # - 'path_depth', 'num_digits'...: Giữ lại hết

    ignore_cols = ['is_ad', 'url', 'domain']

    # Lấy tất cả các cột còn lại làm đầu vào (X)
    feature_cols = [c for c in df.columns if c not in ignore_cols]

    # Kiểm tra xem có cột nào bị NaN (Rỗng) không, nếu có thì điền 0
    df[feature_cols] = df[feature_cols].fillna(0)

    X = df[feature_cols]
    y = df['is_ad']

    print(f"   -> Các đặc trưng sử dụng ({len(feature_cols)} cột):")
    print(f"      {feature_cols}")

    # 3. CHIA DỮ LIỆU
    print("3. Chia tập Train/Test (80/20)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 4. HUẤN LUYỆN
    print("4. Đang huấn luyện Random Forest...")
    # n_estimators=100: 100 cây quyết định
    # class_weight='balanced': Giúp model chú ý hơn đến lớp thiểu số (nếu Ads ít hơn Content)
    clf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    clf.fit(X_train, y_train)

    # 5. ĐÁNH GIÁ
    print("\n" + "=" * 40)
    print("KẾT QUẢ ĐÁNH GIÁ")
    print("=" * 40)

    # Đánh giá trên tập Test
    score = clf.score(X_test, y_test)
    print(f"Độ chính xác (Accuracy): {score * 100:.2f}%")

    y_pred = clf.predict(X_test)
    print("\nChi tiết (Classification Report):")
    print(classification_report(y_test, y_pred, target_names=['SẠCH', 'QUẢNG CÁO']))

    print("Ma trận nhầm lẫn (Confusion Matrix):")
    cm = confusion_matrix(y_test, y_pred)
    print(f" - Đoán đúng là Sạch: {cm[0][0]}")
    print(f" - Đoán nhầm Sạch thành Ads: {cm[0][1]}")
    print(f" - Đoán nhầm Ads thành Sạch: {cm[1][0]} (Nguy hiểm - Bỏ lọt)")
    print(f" - Đoán đúng là Ads: {cm[1][1]}")

    # 6. XEM ĐỘ QUAN TRỌNG CỦA CÁC ĐẶC TRƯNG
    print("\n" + "=" * 40)
    print("TOP YẾU TỐ QUYẾT ĐỊNH (FEATURE IMPORTANCE)")
    print("=" * 40)
    importances = clf.feature_importances_
    indices = np.argsort(importances)[::-1]  # Sắp xếp giảm dần

    for f in range(min(10, len(feature_cols))):  # In top 10
        idx = indices[f]
        print(f"{f + 1}. {feature_cols[idx]}: {importances[idx]:.4f}")

    # 7. LƯU MODEL
    print("\n7. Đang lưu model...")
    # Lưu cả Model và Danh sách tên cột (Để sau này API biết đường mà nhập liệu)
    model_data = {
        "model": clf,
        "feature_names": feature_cols
    }
    joblib.dump(model_data, 'model_hybrid_2026.joblib')
    print("-> Đã lưu thành công: 'model_hybrid_2026.joblib'")
    print("-> Xong! Bạn đã có một bộ não AI xịn xò.")


if __name__ == "__main__":
    main()