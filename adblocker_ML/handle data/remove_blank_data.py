import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

url_1998 = "../ad.data"
cols_1998 = ["height", "width", "aratio", "local"] + [f"url_{i}" for i in range(1554)] + ["is_ad"]
df_1 = pd.read_csv(url_1998, names=cols_1998, low_memory=False, skipinitialspace=True)
df_1 = df_1.replace('?', np.nan)

plt.figure(figsize=(12, 5))
sns.heatmap(df_1.iloc[:, 0:4].isnull(), cbar=False, yticklabels=False, cmap='viridis')
plt.title("Hình 1. Bản đồ nhiệt các giá trị thiếu (Missing values HeatMap) - Dataset 1")
plt.savefig('heatmap_missing.png')

# Bước 3: Loại bỏ hàng bị trống quá 50% thông tin
limit = len(df_1.columns) / 2
df_1 = df_1.dropna(thresh=limit)

print("--- HEATMAP DỮ LIỆU THIẾU VÀ KẾT QUẢ LỌC ---")
print(f"Số lượng mẫu còn lại sau khi lọc hàng khuyết thiếu: {len(df_1)}")
plt.show()