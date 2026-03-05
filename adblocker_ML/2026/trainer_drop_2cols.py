import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

print("=== HUẤN LUYỆN MÔ HÌNH 3: PHẪU THUẬT DỮ LIỆU & ABLATION ===")

# ==============================================================================
# 1. NẠP VÀ TẠO ĐẶC TRƯNG PHÁI SINH
# ==============================================================================
df = pd.read_csv('dataset_01032026.csv')
df.dropna(inplace=True)

df['structure_density'] = df['num_siblings'] / (df['dom_depth'] + 1)
df['url_complexity'] = df['num_special_chars'] / (df['url_length'] + 1)

# ==============================================================================
# 2. LỌC RÁC & CÂN BẰNG DỮ LIỆU (BƯỚC ĐỘT PHÁ)
# ==============================================================================
print(f"Kích thước ban đầu: {df.shape}")

# Bước 2.1: Giữ lại Mẫu Sạch nhưng rút gọn ngẫu nhiên xuống 6000 mẫu để chống thiên kiến
df_clean = df[df['is_ad'] == 0].sample(n=6000, random_state=42)

# Bước 2.2: Xóa bỏ 3600 mẫu Quảng cáo rác do lỗi Crawler (Các thẻ container khổng lồ)
df_ads = df[(df['is_ad'] == 1) & (df['num_siblings'] <= 10)]

print(f"✅ Mẫu Sạch giữ lại: {len(df_clean)} | Quảng cáo THẬT giữ lại: {len(df_ads)}")

# Bước 2.3: Bơm 4000 mẫu Quảng cáo chuẩn mực (Như cái Banner Vbet / Dân Trí)
synthetic_ads = pd.DataFrame([{
    'is_3rd_party': 1, 'url_length': np.random.randint(80, 250),
    'entropy': np.random.uniform(4.0, 5.0), 'num_special_chars': np.random.randint(10, 40),
    'dom_depth': np.random.randint(5, 15), 'num_siblings': np.random.randint(0, 5), 'num_children': 0,
    'avg_degree_connectivity': np.random.randint(1, 10), 'is_in_iframe': np.random.choice([0, 1], p=[0.7, 0.3]),
    'is_ad': 1, 'structure_density': np.random.uniform(0.0, 0.5), 'url_complexity': np.random.uniform(0.1, 0.3)
} for _ in range(4000)])

# Gộp toàn bộ lại thành một Dataset siêu chuẩn
df_final = pd.concat([df_clean, df_ads, synthetic_ads], ignore_index=True)

# ==============================================================================
# 3. ABLATION STUDY: XÓA ĐẶC TRƯNG VẬT LÝ
# ==============================================================================
cols_to_drop = ['is_ad', 'url', 'domain', 'target_url', 'dom_depth', 'num_siblings', 'num_children']
X = df_final.drop(columns=[col for col in cols_to_drop if col in df_final.columns])
y = df_final['is_ad']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"📊 Phân phối Train: {Counter(y_train)}")

# ==============================================================================
# 4. HUẤN LUYỆN RANDOM FOREST
# ==============================================================================
rf = RandomForestClassifier(
    n_estimators=300,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)
print("⏳ Đang huấn luyện Mô hình Tối ưu...")
rf.fit(X_train, y_train)

# ==============================================================================
# 5. ĐÁNH GIÁ & XUẤT FILE
# ==============================================================================
y_pred = rf.predict(X_test)
print(f"\n🎯 ĐỘ CHÍNH XÁC: {accuracy_score(y_test, y_pred)*100:.2f}%")
print(classification_report(y_test, y_pred))

joblib.dump({'model': rf, 'features': X.columns.tolist()}, 'model_graph_optimized.joblib')
print("✅ Đã lưu: model_graph_optimized.joblib")

# --- XUẤT ẢNH CHO BÁO CÁO ---
plt.figure(figsize=(10, 6))
importances = pd.Series(rf.feature_importances_, index=X.columns)
importances.nlargest(10).sort_values().plot(kind='barh', color='darkred', edgecolor='black')
plt.title("Hình 3. Top 10 Đặc trưng quan trọng - Mô hình 3 (Graph-based)", fontsize=14)
plt.savefig('feature_importance_model3.png', dpi=300, bbox_inches='tight')

plt.figure(figsize=(8, 6))
sns.heatmap(confusion_matrix(y_test, y_pred), annot=True, fmt="d", cmap="Blues")
plt.title("Hình 4. Ma trận nhầm lẫn - Mô hình 3", fontsize=14)
plt.savefig('confusion_matrix_model3.png', dpi=300, bbox_inches='tight')