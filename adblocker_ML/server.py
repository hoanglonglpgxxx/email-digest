from fastapi import FastAPI, HTTPException, Query
import pandas as pd
import joblib
import requests
from urllib.parse import urlparse
from PIL import Image
from io import BytesIO
import uvicorn

app = FastAPI(title="AI AdBlocker Smart Scanner")

# 1. LOAD MODEL
print("⏳ Đang load Model...")
try:
    saved_data = joblib.load('model_hybrid_2026.joblib')
    model = saved_data['model']
    trained_features = saved_data['feature_names']
    print("✅ Load thành công!")
except Exception as e:
    print(f"❌ LỖI: {e}")
    exit()


# 2. HÀM TỰ ĐỘNG PHÂN TÍCH LINK (BOT)
def analyze_url_automatically(url: str):
    info = {
        "width": 0,
        "height": 0,
        "request_type": "other"
    }

    # Fake User-Agent xịn hơn để lừa server ảnh
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.google.com/"
    }

    download_success = False

    try:
        # Thử tải ảnh
        response = requests.get(url, headers=headers, timeout=4)  # Tăng timeout xíu

        if response.status_code == 200:
            content_type = response.headers.get("Content-Type", "").lower()

            if "image" in content_type:
                info["request_type"] = "image"
                img = Image.open(BytesIO(response.content))
                info["width"], info["height"] = img.size
                download_success = True

            elif "javascript" in content_type:
                info["request_type"] = "script"
            elif "html" in content_type:
                info["request_type"] = "subdocument"
                info["width"], info["height"] = 1366, 768
                download_success = True

    except Exception as e:
        print(f"   [!] Lỗi tải URL: {e}")

    # --- FAIL-SAFE (QUAN TRỌNG NHẤT) ---
    # Nếu tải thất bại (do bị chặn), ta phải dùng "Trí khôn nhân tạo" để đoán
    if not download_success:
        print("   [!] Không đo được kích thước thật -> Kích hoạt chế độ phỏng đoán (Fail-Safe)")

        # 1. Nếu đuôi file là ảnh thông thường
        if url.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
            info["request_type"] = "image"

            # MẤU CHỐT: Nếu không có từ khóa nhạy cảm, giả định đây là ảnh to
            # (Tránh trường hợp 0x0 bị model hiểu nhầm là Pixel)
            suspicious_keywords = ["ad", "banner", "pixel", "tracker", "doubleclick", "facebook"]
            if not any(k in url.lower() for k in suspicious_keywords):
                info["width"] = 800  # Giả lập kích thước ảnh bài viết
                info["height"] = 600
            else:
                # Nếu có từ khóa 'ad', giữ nguyên 0x0 để Model xử lý
                pass

        elif url.lower().endswith(".js"):
            info["request_type"] = "script"

    return info

def extract_url_features(url):
    try:
        parsed = urlparse(url)
        path = parsed.path
        return {
            "path_depth": path.count('/') if path else 0,
            "url_length": len(url),
            "num_digits": sum(c.isdigit() for c in url),
            "num_params": len(parsed.query.split('&')) if parsed.query else 0
        }
    except:
        return {"path_depth": 0, "url_length": 0, "num_digits": 0, "num_params": 0}


# 3. API ENDPOINT (Dùng GET cho tiện test trên trình duyệt)
@app.get("/scan")
def scan_url(url: str = Query(..., description="Nhập link cần check")):
    print(f"\n🔍 Đang phân tích: {url}")

    # BƯỚC 1: BOT TỰ ĐỘNG QUÉT LINK
    auto_info = analyze_url_automatically(url)
    print(f"   -> Bot phát hiện: Type={auto_info['request_type']} | Size={auto_info['width']}x{auto_info['height']}")

    # BƯỚC 2: TRÍCH XUẤT ĐẶC TRƯNG URL
    url_feats = extract_url_features(url)

    # BƯỚC 3: TẠO DỮ LIỆU INPUT CHO MODEL
    row = {
        "width": auto_info['width'],
        "height": auto_info['height'],

        # One-Hot Encoding
        "req_image": 1 if auto_info['request_type'] == "image" else 0,
        "req_script": 1 if auto_info['request_type'] == "script" else 0,
        "req_subdocument": 1 if auto_info['request_type'] == "subdocument" else 0,
        "req_other": 1 if auto_info['request_type'] == "other" else 0,

        # URL Features
        "path_depth": url_feats['path_depth'],
        "url_length": url_feats['url_length'],
        "num_digits": url_feats['num_digits'],
        "num_params": url_feats['num_params'],

        # Keyword Check
        "has_ad_keyword": 1 if any(x in url.lower() for x in ["ad", "banner", "pixel", "tracker"]) else 0
    }

    # BƯỚC 4: ĐỒNG BỘ CỘT VÀ DỰ ĐOÁN
    df_input = pd.DataFrame([row])
    df_input = df_input.reindex(columns=trained_features, fill_value=0)

    is_ad = model.predict(df_input)[0]
    confidence = model.predict_proba(df_input)[0][1]

    result_text = "QUẢNG CÁO 🚫" if is_ad else "AN TOÀN ✅"
    print(f"   -> Kết luận: {result_text} ({confidence:.1%})")

    return {
        "url": url,
        "analysis": {
            "detected_type": auto_info['request_type'],
            "detected_size": f"{auto_info['width']}x{auto_info['height']}"
        },
        "result": {
            "is_ad": bool(is_ad),
            "confidence": f"{confidence * 100:.2f}%",
            "verdict": result_text
        }
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)