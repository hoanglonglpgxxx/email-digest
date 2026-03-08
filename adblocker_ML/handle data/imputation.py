from sklearn.impute import SimpleImputer
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

url_1998 = "../ad.data"
cols_1998 = ["height", "width", "aratio", "local"] + [f"url_{i}" for i in range(1554)] + ["is_ad"]
df_1 = pd.read_csv(url_1998, names=cols_1998, low_memory=False, skipinitialspace=True)
df_1 = df_1.replace('?', np.nan)
# 1. Áp dụng SimpleImputer cho Tập 1 (Giống bài mẫu trang 9) [cite: 187-188]
imputer = SimpleImputer(missing_values=np.nan, strategy='most_frequent')
df_1.iloc[:, 0:4] = imputer.fit_transform(df_1.iloc[:, 0:4])

# 2. Kiến tạo đặc trưng và Ablation Study cho Tập 3

# Phân tách thành 2 phiên bản cho thực nghiệm
df_2 = pd.read_csv("../2026/dataset_01032026.csv")
df_3 = df_2.copy()

# 1. Thực hiện kiến tạo đặc trưng mới [cite: 156]
df_3['structure_density'] = df_3['num_siblings'] / (df_3['dom_depth'] + 1)
df_3['url_complexity'] = df_3['num_special_chars'] / (df_3['url_length'] + 1)

# 2. Thực hiện Ablation: Loại bỏ cột gây học vẹt (Overfitting)
cols_to_drop = ['dom_depth', 'num_siblings', 'num_children']
df_3_final = df_3.drop(columns=[c for c in cols_to_drop if c in df_3.columns])

# 3. Tạo bảng so sánh để chụp ảnh báo cáo
comparison = pd.DataFrame({
    "Trạng thái": ["Tập 2 (Dữ liệu Thô)", "Tập 3 (Dữ liệu Đồ thị)"],
    "Số lượng đặc trưng": [len(df_2.columns), len(df_3_final.columns)],
    "Đặc trưng Cốt lõi": ["dom_depth, num_siblings", "structure_density (Kiến tạo)"],
    "Mục tiêu": ["Giữ nguyên hiện trạng", "Chống học vẹt Layout (Ablation)"]
})

print("--- KẾT QUẢ IMPUTATION VÀ ABLATION STUDY ---")
print("Đặc trưng Tập 1 sau khi lấp đầy (head):")
print(df_1.iloc[:, 0:4].head())
print(comparison.to_string(index=False))
print("\nChi tiết các cột đã 'thay thế' thành công:")
print(df_3_final.head())