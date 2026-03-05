#Handle image for dataset 1998
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Đọc dữ liệu 1998
url_1998 = "../ad.data"
df_1998 = pd.read_csv(url_1998, header=None, low_memory=False, skipinitialspace=True)
df_1998 = df_1998.iloc[:, [0, 1, 2, 3]] # Chỉ lấy 4 cột kích thước vật lý
df_1998.columns = ["height", "width", "aratio", "local"]

# Chuyển các ký tự "?" thành NaN để vẽ heatmap
df_1998 = df_1998.replace("?", pd.NA)

plt.figure(figsize=(10, 6))
sns.heatmap(df_1998.isnull(), yticklabels=False, cbar=False, cmap='viridis')
plt.title('Hình 1. Bản đồ nhiệt các giá trị thiếu trong Dataset 1998')
plt.savefig('heatmap_1998.png') # Xuất file ảnh ra thư mục dự án
plt.show()