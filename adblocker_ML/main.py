import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

# ==============================================================================
# 4.1. TIỀN XỬ LÝ DỮ LIỆU (DATASET 1) [cite: 151]
# ==============================================================================
url = "ad.data"
# Nạp dữ liệu và đặt tên cột nhãn là 'label'
df = pd.read_csv(url, header=None, low_memory=False)
df.rename(columns={1558: "label"}, inplace=True)

print("--- [4.1] KHỞI TẠO DỮ LIỆU 1998 ---")
print(f"Kích thước ban đầu: {df.shape}")

# ==============================================================================
# 4.2. LOẠI BỎ DỮ LIỆU TRỐNG (VISUALIZATION) [cite: 154, 184]
# ==============================================================================
# Chuyển đổi dấu "?" thành NaN để thư viện Seaborn nhận diện được [cite: 173]
df.replace(r'^\s*\?\s*$', np.nan, regex=True, inplace=True)

# TRỰC QUAN HÓA: Vẽ Heatmap dữ liệu thiếu cho 4 cột kích thước đầu tiên [cite: 167-168]
plt.figure(figsize=(10, 5))
sns.heatmap(df.iloc[:, 0:4].isnull(), cbar=False, yticklabels=False, cmap='viridis')
plt.title("Hình 1. Bản đồ nhiệt các giá trị thiếu (Missing values HeatMap)")
plt.savefig('dataset1_missing_heatmap.png') # Lưu ảnh cho báo cáo
plt.show()

# Loại bỏ các hàng chứa dữ liệu trống
df.dropna(inplace=True)
print(f"Kích thước sau khi loại bỏ dữ liệu trống: {df.shape}")

# ==============================================================================
# 4.3. THAY THẾ & CHUYỂN ĐỔI DỮ LIỆU [cite: 155-156, 193]
# ==============================================================================
# 1. Chuyển đổi nhãn sang dạng nhị phân (0: Sạch, 1: Quảng cáo)
df["label"] = df["label"].apply(lambda x: 1 if x == "ad." else 0)

# 2. Ép kiểu dữ liệu sang dạng số (Numeric) để mô hình có thể tính toán
for col in df.columns:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# 3. Lấp đầy các giá trị phát sinh lỗi bằng trung vị (Median)
df.fillna(df.median(numeric_only=True), inplace=True)

# ==============================================================================
# HUẤN LUYỆN & BÁO CÁO KẾT QUẢ (REPORTING) [cite: 194-206]
# ==============================================================================
X = df.drop("label", axis=1).values
y = df["label"].values
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X_train, y_train)

# Xuất báo cáo hiệu suất chi tiết [cite: 200-204]
y_pred = clf.predict(X_test)
print("\n--- [REPORT] CHI TIẾT HIỆU SUẤT MÔ HÌNH ---")
print(classification_report(y_test, y_pred))

# TRỰC QUAN HÓA: Ma trận nhầm lẫn (Confusion Matrix) [cite: 205]
plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues")
plt.title("Hình 2. Ma trận nhầm lẫn - Random Forest (Dataset 1)")
plt.xlabel("Dự đoán (Predicted)")
plt.ylabel("Thực tế (Actual)")
plt.savefig('dataset1_confusion_matrix.png')
plt.show()