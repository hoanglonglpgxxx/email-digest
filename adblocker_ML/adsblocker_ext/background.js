// ==============================================================================
// 1. CÁC HÀM PHỤ TRỢ (BẮT BUỘC PHẢI CÓ TRONG BACKGROUND.JS)
// ==============================================================================

// Hàm tính toán Entropy để nhận diện DGA hoặc URL làm rối
function getEntropy(str) {
    if (!str) return 0;
    const len = str.length;
    const freq = {};
    for (let char of str) freq[char] = (freq[char] || 0) + 1;
    let entropy = 0;
    for (let char in freq) {
        let p = freq[char] / len;
        entropy -= p * Math.log2(p);
    }
    return entropy;
}

// Hàm đếm ký tự đặc biệt để đánh giá độ phức tạp URL
function countSpecialChars(str) {
    if (!str) return 0;
    const specialChars = str.match(/[^a-zA-Z0-9]/g);
    return specialChars ? specialChars.length : 0;
}

// Hàm kiểm tra Third-party dựa trên Domain gốc
function isThirdParty(url, initiator) {
    try {
        if (!initiator) return 1;
        const mainDomain = new URL(initiator).hostname.split('.').slice(-2).join('.');
        const reqDomain = new URL(url).hostname.split('.').slice(-2).join('.');
        return mainDomain !== reqDomain ? 1 : 0;
    } catch (e) { return 0; }
}

// ==============================================================================
// 2. LẮNG NGHE YÊU CẦU VÀ GIAO TIẾP API
// ==============================================================================

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "predict_ad") {
        // Background đóng vai trò Proxy để vượt rào cản CORS/Mixed Content
        fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request.data)
        })
        .then(res => res.json())
        .then(data => sendResponse({ success: true, data: data }))
        .catch(err => sendResponse({ success: false, error: err.message }));

        return true; // Giữ kênh giao tiếp bất đồng bộ
    }
});

// Lắng nghe sự kiện mạng để phân tích bằng mô hình ONNX (Network Layer)
chrome.webRequest.onBeforeRequest.addListener(
    (details) => {
        if (["image", "sub_frame", "script"].includes(details.type)) {
            const url = details.url;
            if (url.startsWith("data:")) return;

            // Tại đây getEntropy đã được định nghĩa và có thể sử dụng
            const netFeatures = {
                url_length: url.length,
                entropy: getEntropy(url),
                num_special_chars: countSpecialChars(url),
                is_3rd_party: isThirdParty(url, details.initiator)
            };

            console.log("[Network Layer] Đang phân tích URL:", url.substring(0, 50));
            // Tiến trình gọi Offscreen document để chạy ONNX...
        }
    },
    { urls: ["<all_urls>"] }
);