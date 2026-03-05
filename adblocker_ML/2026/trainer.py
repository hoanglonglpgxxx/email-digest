import pandas as pd
import joblib
import seaborn as sns
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from collections import Counter
import matplotlib.pyplot as plt

# ==============================================================================
# 1. NẠP DỮ LIỆU
# ==============================================================================
try:
    df = pd.read_csv('dataset_01032026.csv')
    df.dropna(inplace=True) # Xử lý nhiễu/NaN để tránh lỗi SMOTE
    print("✅ Đã nạp file thành công!")
except FileNotFoundError:
    print("❌ Lỗi: Hãy upload file dữ liệu vào thư mục hiện tại.")
    raise

# ==============================================================================
# 2. TẠO ĐẶC TRƯNG PHÁI SINH
# ==============================================================================
df['structure_density'] = df['num_siblings'] / (df['dom_depth'] + 1)
df['url_complexity'] = df['num_special_chars'] / (df['url_length'] + 1)

# ⚡ ĐIỂM KHÁC BIỆT CỦA TẬP 2: CHỈ XÓA CÁC CỘT TEXT.
# CỐ TÌNH GIỮ LẠI dom_depth, num_siblings, num_children
cols_to_drop = ['is_ad', 'url', 'domain', 'target_url']

X = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
y = df['is_ad']

# ==============================================================================
# 3. CHIA TẬP VÀ ÁP DỤNG SMOTE
# ==============================================================================
# Chia Train/Test TRƯỚC KHI dùng SMOTE để chống rò rỉ dữ liệu
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Dữ liệu tập Train (Trước SMOTE): {Counter(y_train)}")

# Áp dụng SMOTE để sinh mẫu ảo cho Tập 2
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
print(f"⚖️ Dữ liệu tập Train (SAU SMOTE): {Counter(y_train_resampled)}")

# ==============================================================================
# 4. HUẤN LUYỆN MÔ HÌNH 2 (MÔ HÌNH BỊ HỌC VẸT)
# ==============================================================================
# Không giới hạn max_depth, không dùng class_weight để mô hình học thuộc lòng dom_depth
rf_model_2 = RandomForestClassifier(
    n_estimators=300,
    random_state=42,
    n_jobs=-1
)

print("\n⏳ Đang huấn luyện Mô hình 2 (Dữ liệu Lai thô + SMOTE)...")
rf_model_2.fit(X_train_resampled, y_train_resampled)

# ==============================================================================
# 5. ĐÁNH GIÁ TRÊN TẬP TEST
# ==============================================================================
y_pred = rf_model_2.predict(X_test)
print("\n" + "="*30)
print(f"🎯 ĐỘ CHÍNH XÁC (MÔ HÌNH 2): {accuracy_score(y_test, y_pred)*100:.2f}%")
print("="*30)
print("\n--- BÁO CÁO CHI TIẾT ---")
print(classification_report(y_test, y_pred))

# ==============================================================================
# 6. XUẤT FILE JOBLIB THEO YÊU CẦU
# ==============================================================================
storage_model2 = {
    'model': rf_model_2,
    'features': X.columns.tolist()
}
joblib.dump(storage_model2, 'model_raw_smote.joblib')
print("\n✅ Đã lưu model Tập 2 vào file: model_raw_smote.joblib")
print("⚠️ LƯU Ý KHI TEST: Mô hình này yêu cầu ĐẦY ĐỦ các cột đầu vào (bao gồm cả dom_depth, num_siblings).")

# ==============================================================================
# 7. TRỰC QUAN HÓA FEATURE IMPORTANCE
# ==============================================================================
plt.figure(figsize=(12, 7))
importances = pd.Series(rf_model_2.feature_importances_, index=X.columns)
# Dùng màu darkorange để phân biệt với Tập 3
importances.nlargest(10).sort_values().plot(kind='barh', color='darkorange', edgecolor='black')

plt.title("Hình 1. Top 10 Đặc trưng quan trọng - Mô hình 2 (Bị học vẹt Layout)", fontsize=14)
plt.xlabel("Lượng thông tin thu được (Information Gain)", fontsize=12)
plt.grid(axis='x', linestyle='--', alpha=0.7)

# Lưu ảnh chất lượng cao để chèn vào Word
plt.savefig('feature_importance_model2.png', dpi=300, bbox_inches='tight')
print("✅ Đã lưu ảnh: feature_importance_model2.png")
plt.show()

# ==============================================================================
# 8. TRỰC QUAN HÓA MA TRẬN NHẦM LẪN
# ==============================================================================
plt.figure(figsize=(8, 6))
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt="d", cmap="Oranges",
            xticklabels=['Sạch (0)', 'Quảng cáo (1)'],
            yticklabels=['Sạch (0)', 'Quảng cáo (1)'])

plt.title("Hình 2. Ma trận nhầm lẫn - Mô hình 2 (Dùng SMOTE)", fontsize=14)
plt.xlabel("Nhãn dự đoán (Predicted)", fontsize=12)
plt.ylabel("Nhãn thực tế (Actual)", fontsize=12)

# Lưu ảnh ma trận nhầm lẫn
plt.savefig('confusion_matrix_model2.png', dpi=300, bbox_inches='tight')
print("✅ Đã lưu ảnh: confusion_matrix_model2.png")
plt.show()