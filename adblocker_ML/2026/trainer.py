import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from imblearn.over_sampling import SMOTE
from collections import Counter
import matplotlib.pyplot as plt

# 1. Nạp dữ liệu
try:
    df = pd.read_csv('dataset_01032026.csv')
    print("✅ Đã nạp file thành công!")
except FileNotFoundError:
    print("❌ Lỗi:  file 'dataset_01032026.csv' .")
    raise

df['structure_density'] = df['num_siblings'] / (df['dom_depth'] + 1)
df['url_complexity'] = df['num_special_chars'] / (df['url_length'] + 1)

# 2. Tiền xử lý (Xử lý Categorical và lọc cột)
if 'request_type' in df.columns:
    df_numeric = pd.get_dummies(df, columns=['request_type'])
else:
    df_numeric = df.copy()

cols_to_drop = ['is_ad', 'url', 'domain', 'target_url']
X = df_numeric.drop(columns=[col for col in cols_to_drop if col in df_numeric.columns])
y = df_numeric['is_ad']

# 3. CHIA TẬP DỮ LIỆU TRƯỚC (Chống Data Leakage)
# Việc chia trước giúp tập Test hoàn toàn là dữ liệu thực, không có mẫu ảo
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Dữ liệu gốc tập Train: {Counter(y_train)}")

# 4. SMOTE (Chỉ áp dụng trên tập TRAIN)
smote = SMOTE(sampling_strategy=0.6, random_state=42)
X_train_res, y_train_res = smote.fit_resample(X_train, y_train)
print(f"📈 Sau SMOTE (chỉ tập Train): {Counter(y_train_res)}")

# 5. Huấn luyện Random Forest
# n_jobs=-1 để tận dụng tối đa CPU của Colab
rf_model = RandomForestClassifier(
    n_estimators=400,
    max_depth=12,  # Giảm độ sâu để ép mô hình học "quy luật chung"
    min_samples_leaf=20,  # Mỗi lá phải có ít nhất 10 mẫu (tránh học vẹt)
    max_features='sqrt',  # Giới hạn số đặc trưng mỗi lần chia
    random_state=42,
    n_jobs=-1,
    class_weight=None  # Vì đã dùng SMOTE 0.6 nên không cần cái này nữa
)
rf_model.fit(X_train_res, y_train_res)

# 6. Đánh giá trên tập TEST thực tế
y_pred = rf_model.predict(X_test)
print("\n" + "="*30)
print(f"🎯 ĐỘ CHÍNH XÁC THỰC TẾ: {accuracy_score(y_test, y_pred)*100:.2f}%")
print("="*30)
print("\n--- BÁO CÁO CHI TIẾT ---")
print(classification_report(y_test, y_pred))

# 7. XUẤT FILE JOBLIB (Để sử dụng cho NodeShield)
storage = {
    'model': rf_model,
    'features': X.columns.tolist()
}
joblib.dump(storage, '2026_train_01032026.joblib')
print("\n✅ Đã lưu model vào file: 2026_train_01032026.joblib")

# 8. Trực quan hóa Feature Importance
plt.figure(figsize=(10, 6))
importances = pd.Series(rf_model.feature_importances_, index=X.columns)
importances.nlargest(10).sort_values().plot(kind='barh', color='darkblue')
plt.title("Top 10 Đặc trưng quan trọng (Random Forest)")
plt.show()