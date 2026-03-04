// 1. Các hàm tính toán đặc trưng DOM
function getDepth(el) {
    let depth = 0;
    while (el.parentNode) { el = el.parentNode; depth++; }
    return depth;
}

function getConnectivity(el) {
    let siblings = el.parentElement ? el.parentElement.children.length - 1 : 0;
    let children = el.children.length;
    return 1 + siblings + children;
}

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

function isThirdParty(url) {
    try {
        const mailDomain = window.location.hostname.split('.').slice(-2).join('.');
        const adDomain = new URL(url).hostname.split('.').slice(-2).join('.');
        return mailDomain !== adDomain ? 1 : 0;
    } catch (e) { return 0; }
}

// 2. Hàm tạo khối Placeholder "BLOCKED"
function showBlockedPlaceholder(el) {
    const width = el.offsetWidth || el.width || 300;
    const height = el.offsetHeight || el.height || 250;

    const placeholder = document.createElement('div');
    placeholder.style.width = width + 'px';
    placeholder.style.height = height + 'px';
    placeholder.style.backgroundColor = '#f8d7da';
    placeholder.style.border = '2px dashed #dc3545';
    placeholder.style.color = '#721c24';
    placeholder.style.display = 'inline-flex';
    placeholder.style.flexDirection = 'column';
    placeholder.style.alignItems = 'center';
    placeholder.style.justifyContent = 'center';
    placeholder.style.fontSize = '12px';
    placeholder.style.fontWeight = 'bold';
    placeholder.style.fontFamily = 'Segoe UI, Tahoma, sans-serif';
    placeholder.style.textAlign = 'center';
    placeholder.style.margin = '5px';
    placeholder.innerHTML = `
        <span style="font-size: 20px;">🛡️</span>
        <div style="margin-top: 5px;">ADBLOCKER AI</div>
        <div style="font-size: 10px; color: #dc3545;">[BLOCKED]</div>
    `;

    el.parentNode.insertBefore(placeholder, el);
    el.style.display = 'none';
}

// 3. Quét và dự đoán (Lớp DOM)
async function scanAndBlock() {
    const elements = document.querySelectorAll("img, iframe, ins.adsbygoogle, div[id*='ads']");

    for (let el of elements) {
        if (el.dataset.aiChecked) continue;
        el.dataset.aiChecked = "true";

        const url = el.src || el.getAttribute('data-ad-client') || "";

        // Lọc nội bộ để tránh gọi API thừa
        if (url.startsWith('data:image/svg+xml') || url.includes(window.location.hostname)) {
            continue;
        }

        const features = {
            "url": url,
            "dom_depth": getDepth(el),
            "avg_degree_connectivity": getConnectivity(el),
            "num_siblings": el.parentElement ? el.parentElement.children.length - 1 : 0,
            "url_length": url.length,
            "entropy": getEntropy(url),
            "num_special_chars": countSpecialChars(url),
            "is_3rd_party": isThirdParty(url),
            "is_in_iframe": window.self !== window.top ? 1 : 0
        };

        try {
            // Gửi dữ liệu cấu trúc cho Python Server đang chạy Local
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(features)
            });
            const data = await response.json();

            if (data.is_ad) {
                console.log(`[DOM Layer] 🛡️ AI Detected Ads (${(data.probability * 100).toFixed(2)}%):`, url);
                showBlockedPlaceholder(el);
            }
        } catch (e) { /* Bỏ qua nếu server tắt */ }
    }
}

// 4. Lắng nghe sự kiện Alt + Click để Audit
window.addEventListener('mousedown', async (e) => {
    if (e.altKey && e.button === 0) {
        const el = e.target.closest('img, iframe, a');
        if (!el) return;

        e.preventDefault();
        e.stopImmediatePropagation();

        const targetEl = e.target.tagName === 'IMG' ? e.target : el;
        const url = targetEl.src || targetEl.href || "";

        const features = {
            "dom_depth": getDepth(targetEl),
            "avg_degree_connectivity": getConnectivity(targetEl),
            "num_siblings": targetEl.parentElement ? targetEl.parentElement.children.length - 1 : 0,
            "url_length": url.length,
            "entropy": getEntropy(url),
            "num_special_chars": countSpecialChars(url),
            "is_3rd_party": isThirdParty(url),
            "is_in_iframe": window.self !== window.top ? 1 : 0
        };

        try {
            const response = await fetch('http://127.0.0.1:8000/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(features)
            });
            const data = await response.json();

            const status = data.is_ad ? "ADS ❌" : "SẠCH ✅";
            const prob = (data.probability * 100).toFixed(4);

            alert(`--- KẾT QUẢ PHÂN TÍCH LỚP DOM ---\nDự đoán: ${status}\nXác suất Ads: ${prob}%\n\nĐặc trưng trích xuất:\n- Depth: ${features.dom_depth}\n- Connectivity: ${features.avg_degree_connectivity}\n- Entropy: ${features.entropy.toFixed(2)}`);
        } catch (err) {
            console.error("Lỗi API Local:", err);
        }
    }
}, true);

// Khởi chạy
scanAndBlock();
setInterval(scanAndBlock, 3000);