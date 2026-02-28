# Tìm ra 1 mẫu Ads mà mô hình tự tin nhất (Xác suất gần 1.0)
import pandas as pd
df = pd.read_csv('dataset_hybrid_2026_advanced.csv')

# Lọc ra các mẫu là Ads thật (is_ad == 1)
ads_only = df[df['is_ad'] == 1]

# Lấy mẫu có dom_depth phổ biến nhất của Ads
typical_ad = ads_only.sample(1)
print("--- HÃY DÙNG BỘ SỐ NÀY ĐỂ CURL ---")
print(typical_ad[['dom_depth', 'avg_degree_connectivity', 'num_siblings', 'url_length', 'entropy', 'is_3rd_party', 'num_special_chars']].to_dict('records')[0])