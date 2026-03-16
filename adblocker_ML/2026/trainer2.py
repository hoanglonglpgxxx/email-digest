import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from collections import Counter
import matplotlib.pyplot as plt

# 1. Nạp dữ liệu
try:
    df = pd.read_csv('data_enrich.csv')
    print("✅ Đã nạp file thành công!")
except FileNotFoundError:
    print("❌ Lỗi: Hãy upload file 'data_enrich.csv' vào Colab.")
    raise

# 2. Tạo đặc trưng phái sinh (Feature Engineering)
df['structure_density'] = df['num_siblings'] / (df['dom_depth'] + 1)
df['url_complexity'] = df['num_special_chars'] / (df['url_length'] + 1)

# Tiền xử lý Categorical
if 'request_type' in df.columns:
    df_numeric = pd.get_dummies(df, columns=['request_type'])
else:
    df_numeric = df.copy()

# -------------------------------------------------------------
# ⚡ SỬA LỖI 1: BẮT BUỘC XÓA CÁC CỘT LÀM MÔ HÌNH HỌC VẸT
# -------------------------------------------------------------
cols_to_drop = [
    'is_ad', 'url', 'domain', 'target_url',
    'dom_depth', 'num_siblings'   # <--- Đưa vào để ép model dùng data làm giàu
]
X = df_numeric.drop(columns=[col for col in cols_to_drop if col in df_numeric.columns])
y = df_numeric['is_ad']

# 3. CHIA TẬP DỮ LIỆU
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Dữ liệu tập Train: {Counter(y_train)}")

# -------------------------------------------------------------
# ⚡ SỬA LỖI 2 & 3: BỎ SMOTE VÀ TINH CHỈNH HYPERPARAMETERS
# -------------------------------------------------------------
rf_model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,            # Tăng nhẹ độ sâu để model học được các quy luật JS tinh vi
    min_samples_leaf=15,     # Giảm xuống 15 để tránh Underfitting (không để 100)
    max_features='log2',     # Ép thuật toán phải nhìn vào các đặc trưng JavaScript mới
    class_weight='balanced_subsample', # Thay thế hoàn hảo cho SMOTE đối với Random Forest
    random_state=42,
    n_jobs=-1
)

print("⏳ Đang huấn luyện mô hình (Không dùng SMOTE, dùng Class Weight)...")
rf_model.fit(X_train, y_train)

# 4. Đánh giá trên tập TEST thực tế
y_pred = rf_model.predict(X_test)
print("\n" + "="*30)
print(f"🎯 ĐỘ CHÍNH XÁC THỰC TẾ: {accuracy_score(y_test, y_pred)*100:.2f}%")
print("="*30)
print("\n--- BÁO CÁO CHI TIẾT ---")
print(classification_report(y_test, y_pred))

# 5. XUẤT FILE JOBLIB
storage = {
    'model': rf_model,
    'features': X.columns.tolist()
}
joblib.dump(storage, 'data_enriched_LATEST.joblib')
print("\n✅ Đã lưu model vào file: data_enriched_LATEST.joblib")

# 6. Trực quan hóa Feature Importance
plt.figure(figsize=(10, 6))
importances = pd.Series(rf_model.feature_importances_, index=X.columns)
importances.nlargest(10).sort_values().plot(kind='barh', color='darkred')
plt.title("Top 10 Đặc trưng quan trọng (Tập Data Làm Giàu)")
plt.xlabel("Lượng thông tin thu được (Information Gain)")
plt.show()