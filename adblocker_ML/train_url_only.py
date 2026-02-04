import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from features import extract_features # Import hàm ở trên

# Giả sử bạn đã có file CSV chỉ gồm 2 cột: 'url' và 'is_ad'
# (Bạn có thể dùng file dataset_hybrid_2026.csv cũ để trích ra)

print("Đang xử lý dữ liệu...")
df = pd.read_csv("dataset_hybrid_2026.csv")

# Tạo dataset mới từ features
X_rows = []
for url in df['url']:
    X_rows.append(extract_features(url))

X = pd.DataFrame(X_rows)
y = df['is_ad']

print("Đang train...")
clf = RandomForestClassifier(n_estimators=100, random_state=42)
clf.fit(X, y)

joblib.dump(clf, "model_url_classifier.joblib")
print("Xong! Model này chỉ nhìn URL là bắt được bài.")