// --- CÁC HÀM TRÍCH XUẤT ĐẶC TRƯNG URL ---
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

function countSpecialChars(str) {
    if (!str) return 0;
    const specialChars = str.match(/[^a-zA-Z0-9]/g);
    return specialChars ? specialChars.length : 0;
}

function isThirdParty(url, initiator) {
    try {
        if (!initiator) return 1;
        const mainDomain = new URL(initiator).hostname.split('.').slice(-2).join('.');
        const reqDomain = new URL(url).hostname.split('.').slice(-2).join('.');
        return mainDomain !== reqDomain ? 1 : 0;
    } catch (e) { return 0; }
}

// --- QUẢN LÝ OFFSCREEN DOCUMENT ---
let creating;
async function setupOffscreenDocument(path) {
    const offscreenUrl = chrome.runtime.getURL(path);
    const existingContexts = await chrome.runtime.getContexts({
        contextTypes: ['OFFSCREEN_DOCUMENT'],
        documentUrls: [offscreenUrl]
    });
    if (existingContexts.length > 0) return;
    if (creating) {
        await creating;
    } else {
        creating = chrome.offscreen.createDocument({
            url: path,
            reasons: ['WORKERS'],
            justification: 'Chạy mô hình AI ONNX để dự đoán URL'
        });
        await creating;
        creating = null;
    }
}

// Gửi dữ liệu sang Off-screen để AI phân tích
async function checkWithAI(features) {
    await setupOffscreenDocument('offscreen.html');
    return new Promise((resolve) => {
        chrome.runtime.sendMessage(
            { type: "AI_PREDICT", features: features },
            (response) => resolve(response ? response.isAd : false)
        );
    });
}

// --- LẮNG NGHE YÊU CẦU MẠNG ---
chrome.webRequest.onBeforeRequest.addListener(
    async (details) => {
        if (details.type === "image" || details.type === "sub_frame" || details.type === "script") {
            const url = details.url;

            // Bỏ qua các URL dạng data: base64
            if (url.startsWith("data:")) return;

            const features = {
                url_length: url.length,
                entropy: getEntropy(url),
                num_special_chars: countSpecialChars(url),
                is_3rd_party: isThirdParty(url, details.initiator)
                // Đảm bảo số lượng features này khớp với Tensor [1, 4] hoặc [1, 8] của model ONNX
            };

            const isAd = await checkWithAI(features);

            if (isAd) {
                console.log(`[Network Layer] Phát hiện Ads URL, tạo luật chặn: ${url.substring(0, 50)}...`);
                // Tạo luật chặn động bằng declarativeNetRequest
                const ruleId = Math.floor(Math.random() * 90000) + 10000; // Tránh trùng ID
                chrome.declarativeNetRequest.updateDynamicRules({
                    addRules: [{
                        id: ruleId,
                        priority: 1,
                        action: {type: "block"},
                        condition: {
                            urlFilter: url.split('?')[0], // Chặn theo base URL để tăng tính tổng quát
                            resourceTypes: ["image", "sub_frame", "script"]
                        }
                    }]
                });
            }
        }
    },
    {urls: ["<all_urls>"]}
);