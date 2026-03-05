import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Cấu hình hiển thị bảng dữ liệu trên Console PyCharm
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# 1. Nạp tập dữ liệu thực tế (29k mẫu)
# Đảm bảo file CSV này nằm cùng thư mục với script
df = pd.read_csv('dataset_hybrid_2026_advanced.csv')

# 2. Thiết lập đặc trưng cho Mô hình 3 (Graph-based)
# Nhóm URL: url_length, entropy, num_special_chars
# Nhóm Đồ thị: avg_degree_connectivity, num_siblings, num_children
selected_features = [
    'url_length', 'entropy', 'num_special_chars',
    'avg_degree_connectivity', 'num_siblings', 'num_children',
    'is_ad'
]

# 3. Thực hiện Ablation Study: Loại bỏ dom_depth
# Việc chỉ trích xuất các cột trong selected_features đã tự động loại bỏ dom_depth
df_model3 = df[selected_features].copy()

print("--- ẢNH 3: MÔ HÌNH 3 (LÀM GIÀU ĐỒ THỊ - GRAPH-BASED) ---")
print("Dữ liệu sau khi thực hiện Ablation Study (Loại bỏ hoàn toàn dom_depth):")
print(df_model3.head(10))

# 4. Xuất sơ đồ Ma trận tương quan (Correlation Matrix)
plt.figure(figsize=(10, 8))
# Tính toán ma trận tương quan Pearson
corr = df_model3.corr()

# Vẽ Heatmap chuyên nghiệp cho báo cáo
sns.heatmap(corr, annot=True, cmap='YlGnBu', fmt=".2f", linewidths=0.5)
plt.title('Hình 3. Ma trận tương quan đặc trưng Đồ thị và URL (Mô hình 3)')

# Lưu ảnh để dán vào file Word báo cáo
plt.savefig('graph_based_correlation.png', dpi=300, bbox_inches='tight')
print("\n✅ Đã xuất sơ đồ: graph_based_correlation.png")
plt.show()