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
    df = pd.read_csv('dataset_01032026.csv')
    print("✅ Đã nạp file thành công!")
except FileNotFoundError:
    print("❌ Lỗi: không tìm thấy file.")
    raise

# 2. Tạo đặc trưng phái sinh tổng quát hóa cấu trúc
# +1 để tránh lỗi chia cho 0
df['structure_density'] = df['num_siblings'] / (df['dom_depth'] + 1)
df['url_complexity'] = df['num_special_chars'] / (df['url_length'] + 1)

if 'request_type' in df.columns:
    df_numeric = pd.get_dummies(df, columns=['request_type'])
else:
    df_numeric = df.copy()

# -------------------------------------------------------------
# QUAN TRỌNG: Phải XÓA CÁC CỘT GÂY OVERFIT LAYOUT
# -------------------------------------------------------------
cols_to_drop = [
    'is_ad', 'url', 'domain', 'target_url', 
    'dom_depth', 'num_siblings', 'num_children' # <--- Xóa các cột này để ép mô hình học tổng quát
]
X = df_numeric.drop(columns=[col for col in cols_to_drop if col in df_numeric.columns])
y = df_numeric['is_ad']

# 3. Chia tập dữ liệu
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Phân bổ nhãn tập Train: {Counter(y_train)}")

# 4. Huấn luyện Random Forest TỐI ƯU
# KHÔNG DÙNG SMOTE nữa vì RF kết hợp class_weight='balanced' thường tốt hơn cho dữ liệu có categorical/discrete features.
rf_model = RandomForestClassifier(
    n_estimators=400,
    max_depth=10,            # Ép cây nông hơn nữa để bắt buộc học các quy luật lớn
    min_samples_leaf=15,     # Tăng min_samples_leaf để tránh các cụm dữ liệu quá nhỏ (học vẹt)
    max_features='sqrt',
    random_state=42,
    n_jobs=-1,
    class_weight='balanced_subsample' # <--- Dùng cái này thay cho SMOTE. Thuật toán sẽ tự tăng trọng số cho nhãn thiểu số (ads).
)

print("⏳ Đang huấn luyện mô hình...")
rf_model.fit(X_train, y_train)

# 5. Đánh giá
y_pred = rf_model.predict(X_test)
print("\n" + "="*30)
print(f"🎯 ĐỘ CHÍNH XÁC THỰC TẾ: {accuracy_score(y_test, y_pred)*100:.2f}%")
print("="*30)
print("\n--- BÁO CÁO CHI TIẾT ---")
print(classification_report(y_test, y_pred))

# 6. Trực quan hóa Feature Importance
plt.figure(figsize=(10, 6))
importances = pd.Series(rf_model.feature_importances_, index=X.columns)
importances.nlargest(10).sort_values().plot(kind='barh', color='darkgreen')
plt.title("Top 10 Đặc trưng quan trọng (Đã loại bỏ nhiễu Layout)")
plt.show()

# 7. Xuất file
storage = {
    'model': rf_model,
    'features': X.columns.tolist()
}
joblib.dump(storage, '2026_train_rf_optimized.joblib')