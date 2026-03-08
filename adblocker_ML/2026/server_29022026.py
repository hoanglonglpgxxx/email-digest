from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd

app = FastAPI()

# Cho phép Extension truy cập vào API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,  # Bật thêm cái này cho an toàn
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model bạn đã train (Mô hình 3 tối ưu)
data = joblib.load('model_graph_optimized.joblib')
model = data['model']
features = data['features']


@app.post("/predict")
async def predict(request: Request):
    # Dùng await request.json() để parse body trực tiếp, tránh lỗi 422 của FastAPI
    req = await request.json()

    # In ra Terminal để xác nhận Server ĐÃ NHẬN ĐƯỢC DATA từ Extension
    print("\n[+] Đã nhận request từ Extension:", req)

    # Tính toán 2 đặc trưng mới ngay tại Server (Chuẩn xác!)
    req['structure_density'] = req['num_siblings'] / (req['dom_depth'] + 1)
    req['url_complexity'] = req['num_special_chars'] / (req['url_length'] + 1)

    # Đưa vào DataFrame và sắp xếp lại cột chuẩn form lúc Train
    df = pd.DataFrame([req])
    df = df.reindex(columns=features, fill_value=0)
    probs = model.predict_proba(df)

    # Truy cập: [Hàng đầu tiên][Cột thứ hai (Nhãn 1)]
    prob = probs[0][1]

    # Áp dụng ngưỡng (Threshold) để giảm tỷ lệ chặn nhầm (False Positive)
    is_ad = 1 if prob >= 0.6 else 0

    print(f"==> Kết quả: {'QUẢNG CÁO' if is_ad else 'SẠCH'} (Xác suất: {prob * 100:.2f}%)")

    return {"is_ad": bool(is_ad), "probability": float(prob)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)