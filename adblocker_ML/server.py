from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
from features import extract_features

app = FastAPI()
model = joblib.load("model_url_classifier.joblib")


class Link(BaseModel):
    url: str


@app.post("/check")
def check(link: Link):
    # 1. Trích xuất đặc trưng từ chuỗi URL
    feats = extract_features(link.url)

    # 2. Tạo DataFrame
    df = pd.DataFrame([feats])

    # 3. Dự đoán
    is_ad = model.predict(df)[0]
    prob = model.predict_proba(df)[0][1]

    return {
        "url": link.url,
        "features": feats,
        "is_ad": bool(is_ad),
        "confidence": f"{prob:.2%}"
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)