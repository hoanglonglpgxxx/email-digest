import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier
import joblib
import time


def main():
    # --- Step 1 & 2: Load dữ liệu ---
    print("1. Đang đọc dữ liệu từ file 'ad.data'...")
    # low_memory=False giúp tránh lỗi warning vì dữ liệu có lẫn lộn số và ký tự "?"
    try:
        df = pd.read_csv("ad.data", header=None, low_memory=False)
    except FileNotFoundError:
        print("LỖI: Không tìm thấy file 'ad.data'. Hãy tải nó về và để cùng thư mục với file code này.")
        return

    # Đổi tên cột cuối cùng (cột 1558) thành 'label' để dễ gọi
    df.rename(columns={1558: "label"}, inplace=True)

    # --- Step 3 & 4: Làm sạch dữ liệu (Xử lý giá trị thiếu '?') ---
    print("2. Đang tìm và xóa các dòng lỗi (chứa ký tự '?')...")
    print("   Lưu ý: Bước này có thể mất vài chục giây tùy tốc độ máy.")

    start_time = time.time()

    # Cách trong sách dùng vòng lặp for (khá chậm), nhưng mình giữ nguyên logic để bạn dễ hiểu
    # Tuy nhiên, ta chuyển đổi toàn bộ về string trước để tránh lỗi kiểu dữ liệu
    improper_rows = []

    # Duyệt qua từng hàng (iterrows)
    for index, row in df.iterrows():
        # Kiểm tra nhanh: Nếu dòng này có chứa "?" thì đánh dấu luôn
        # (Dùng map để kiểm tra toàn bộ dòng nhanh hơn for lồng nhau)

        # if row.astype(str).str.contains(r'\?').any():
        #     improper_rows.append(index)

        for col in df.columns:
            val = str(row[col]).strip()
            if val == "?":
                improper_rows.append(index)

    # Xóa các dòng bị lỗi
    df = df.drop(df.index[improper_rows])

    print(f"   -> Đã xóa {len(improper_rows)} dòng lỗi.")
    print(f"   -> Thời gian xử lý: {time.time() - start_time:.2f} giây.")

    # --- Step 5: Chuyển đổi nhãn (Label) sang số ---
    # 1: Là quảng cáo (ad.), 0: Không phải quảng cáo
    print("3. Chuyển đổi nhãn sang dạng số (0 và 1)...")

    def label_to_numeric(row):
        # strip() để cắt bỏ khoảng trắng thừa nếu có
        if str(row["label"]).strip() == "ad.":
            return 1
        else:
            return 0

    df["label"] = df.apply(label_to_numeric, axis=1)

    # --- Step 6: Chia dữ liệu Train/Test ---
    print("4. Chia dữ liệu train/test...")
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)

    # --- Step 7: Tách Feature (X) và Label (y) ---
    # pop() sẽ lấy cột label ra và xóa nó khỏi df ban đầu, trả về array
    y_train = df_train.pop("label").values
    y_test = df_test.pop("label").values

    # Phần còn lại là X (features)
    # Cần chuyển về dạng số thực (float) vì mô hình không hiểu string
    # Lúc đọc vào có "?" nên pandas hiểu là string, giờ sạch rồi thì ép kiểu về float
    X_train = df_train.astype(float).values
    X_test = df_test.astype(float).values

    # --- Step 8: Huấn luyện mô hình ---
    print("5. Đang huấn luyện Random Forest...")
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)

    # --- Step 9: Đánh giá ---
    print("6. Đang chấm điểm trên tập Test...")
    score = clf.score(X_test, y_test)
    print("=" * 30)
    print(f"KẾT QUẢ ĐỘ CHÍNH XÁC (Test Set): {score * 100:.2f}%")
    print("=" * 30)

    # ==============================================================================
    # [PHẦN MỚI THÊM VÀO] KIỂM CHỨNG CHÉO (CROSS-VALIDATION)
    # ==============================================================================
    print("\n[KIỂM TRA SÂU] Đang chạy K-Fold Cross Validation (5 lần)...")
    # cv=5: Chia dữ liệu làm 5 phần, máy sẽ học 5 lần khác nhau để xem phong độ có ổn định không
    cv_scores = cross_val_score(clf, X_train, y_train, cv=5)

    print(f"   -> Điểm số 5 lần chạy: {cv_scores}")
    print(f"   -> ĐỘ CHÍNH XÁC TRUNG BÌNH: {cv_scores.mean() * 100:.2f}% (+/- {cv_scores.std() * 100:.2f}%)")
    print("=" * 30 + "\n")
    # ==============================================================================

    print("7. Đang lưu model vào file 'ad_blocker_model.joblib'...")
    joblib.dump(clf, 'ad_blocker_model.joblib')
    print("--> Đã lưu thành công! Bạn có thể tắt chương trình.")

if __name__ == "__main__":
    main()