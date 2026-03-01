from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import joblib
import pandas as pd
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("adblocker-Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

try:
    data = joblib.load('2026_train_rf_optimized.joblib')
    model = data['model']
    features = data['features']
    logger.info("✅ Đã nạp thành công model 2026_value_5")
except Exception as e:
    logger.error(f"❌ Lỗi nạp model: {e}")

DOMAIN_WHITELIST = ["dantri.com.vn", "vnexpress.net", "vietnamnet.vn"]


@app.post("/predict")
async def predict(req: dict):
    url = req.get('url', '')

    if any(domain in url for domain in DOMAIN_WHITELIST):
        return {"is_ad": False, "probability": 0.0, "reason": "whitelist"}

    depth = req.get('dom_depth', 0)
    url_len = req.get('url_length', 0)

    req['structure_density'] = req.get('num_siblings', 0) / (depth + 1)
    req['url_complexity'] = req.get('num_special_chars', 0) / (url_len + 1)

    df = pd.DataFrame([req])
    df = df.reindex(columns=features, fill_value=0)

    prob = model.predict_proba(df)[0][1]

    threshold = 0.85
    is_ad = 1 if prob >= threshold else 0

    if is_ad:
        logger.info(f"🛡️ BLOCKED ({prob:.2f}): {url[:50]}...")

    return {
        "is_ad": bool(is_ad),
        "probability": float(prob),
        "threshold_used": threshold
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)