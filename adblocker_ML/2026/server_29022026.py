from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# data = joblib.load('../../final_adblocker/dataset3/model3_final.joblib')
data = joblib.load('../../final_adblocker/dataset3/demo3.joblib')
model = data['model']
features = data['features']


@app.post("/predict")
async def predict(request: Request):
    req = await request.json()

    print("\n[+] Đã nhận request từ Extension:", req)

    # Tính toán 2 đặc trưng mới ngay tại Server (Chuẩn xác!)
    req['structure_density'] = req['num_siblings'] / (req['dom_depth'] + 1)
    req['url_complexity'] = req['num_special_chars'] / (req['url_length'] + 1)

    # Đưa vào DataFrame và sắp xếp lại cột chuẩn form lúc Train
    df = pd.DataFrame([req])
    df = df.reindex(columns=features, fill_value=0)
    probs = model.predict_proba(df)

    prob = probs[0][1]

    # Áp dụng ngưỡng (Threshold) để giảm tỷ lệ chặn nhầm (False Positive)
    is_ad = 1 if prob >= 0.6 else 0

    print(f"==> Kết quả: {'QUẢNG CÁO' if is_ad else 'SẠCH'} (Xác suất: {prob * 100:.2f}%)")

    return {"is_ad": bool(is_ad), "probability": float(prob)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)