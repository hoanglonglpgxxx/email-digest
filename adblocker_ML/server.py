from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import pandas as pd
import uvicorn
import math
from collections import Counter
from urllib.parse import urlparse
import tldextract

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Load model Random Forest đã train
try:
    data = joblib.load("model_final_2026.joblib")
    model = data['model']
    trained_features = data['feature_names']
    print("-> AI Model Loaded.")
except:
    print("-> Model file not found!")


class AdRequest(BaseModel):
    url: str
    target_url: str = ""
    width: int = 0
    height: int = 0
    source_domain: str = ""


def calculate_entropy(text):
    if not text: return 0
    counter = Counter(text)
    length = len(text)
    return -sum((count / length) * math.log2(count / length) for count in counter.values())


@app.post("/check")
async def check(data: AdRequest):
    try:
        url_to_check = data.target_url if data.target_url else data.url
        parsed = urlparse(url_to_check)

        # 1. Heuristics cho cá cược (Bet)
        target_lower = url_to_check.lower()
        bet_keywords = ['bet', 'casino', 'nha-cai', 'shbet', '789bet', 'viva88', 'khuyen-mai']
        if any(kw in target_lower for kw in bet_keywords):
            return {"is_ad": True, "confidence": "100%", "reason": "Bet Keyword"}

        # 2. Đặc trưng cho AI
        feats = {
            "path_depth": int(parsed.path.count('/')),
            "url_length": int(len(url_to_check)),
            "num_digits": int(sum(c.isdigit() for c in url_to_check)),
            "entropy": float(calculate_entropy(url_to_check)),
            "num_params": int(len(parsed.query.split('&')) if parsed.query else 0),
        }

        # 3. Dự đoán (Fix lỗi NumPy)
        df = pd.DataFrame([feats]).reindex(columns=trained_features, fill_value=0)
        prob = float(model.predict_proba(df)[0][1])
        is_ad_ai = bool(model.predict(df)[0])

        # 4. Kiểm tra nguồn gốc (First-party vs Third-party)
        res_domain = tldextract.extract(url_to_check).domain
        src_domain = tldextract.extract(data.source_domain).domain
        is_first_party = bool(res_domain == src_domain)

        # Chặn nếu AI nghi ngờ > 45% cho bên thứ 3
        return {
            "is_ad": bool(prob > 0.45 and not is_first_party),
            "confidence": f"{prob:.2%}"
        }
    except Exception as e:
        return {"is_ad": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)