from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd

app = FastAPI()

# Cho phép Extension truy cập vào API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model bạn đã train
data = joblib.load('data_enriched_v1.joblib')
model = data['model']
features = data['features']


@app.post("/predict")
async def predict(req: dict):
    # Tính toán 2 đặc trưng mới ngay tại Server
    req['structure_density'] = req['num_siblings'] / (req['dom_depth'] + 1)
    req['url_complexity'] = req['num_special_chars'] / (req['url_length'] + 1)

    df = pd.DataFrame([req])
    df = df.reindex(columns=features, fill_value=0)

    prob = model.predict_proba(df)[0][1]
    is_ad = 1 if prob >= 0.7 else 0

    return {"is_ad": bool(is_ad), "probability": float(prob)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)