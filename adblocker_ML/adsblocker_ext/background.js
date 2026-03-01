chrome.webRequest.onBeforeRequest.addListener(
    async (details) => {
        if (details.type === "image" || details.type === "sub_frame") {
            const url = details.url;
            const features = {
                url_length: url.length,
                entropy: getEntropy(url), // Dùng hàm Entropy bạn đã viết
                num_special_chars: countSpecialChars(url),
                is_3rd_party: isThirdParty(url, details.initiator)
            };

            // Gửi sang Off-screen tab để AI dự đoán bằng ONNX
            const isAd = await checkWithAI(features);

            if (isAd) {
                // Tạo luật chặn động ngay lập tức
                chrome.declarativeNetRequest.updateDynamicRules({
                    addRules: [{
                        id: Math.floor(Math.random() * 10000),
                        priority: 1,
                        action: { type: "block" },
                        condition: { urlFilter: url, resourceTypes: ["image", "sub_frame"] }
                    }]
                });
            }
        }
    },
    { urls: ["<all_urls>"] }
);