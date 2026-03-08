import pandas as pd

# 1. Nạp tập dữ liệu Baseline 1998 từ UCI
url_1998 = "../ad.data"
cols_1998 = ["height", "width", "aratio", "local"] + [f"url_{i}" for i in range(1554)] + ["is_ad"]
df_1 = pd.read_csv(url_1998, names=cols_1998, low_memory=False, skipinitialspace=True)

# 2. Nạp tập dữ liệu tự thu thập (NodeShield v1)
df_raw = pd.read_csv("../2026/dataset_01032026.csv")

# Phân tách thành 2 phiên bản cho thực nghiệm
df_2 = df_raw.copy()
df_3 = df_raw.copy()

print("--- KHỞI TẠO 3 TẬP DỮ LIỆU ĐỘC LẬP ---")
print(f"Dataset 1 (Baseline 1998): {df_1.shape}")
print(f"Dataset 2 (Hybrid Raw): {df_2.shape}")
print(f"Dataset 3 (Graph-based): {df_3.shape}")