// 1. Các hàm tính toán đặc trưng (Features Extraction)
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

// Tính Entropy của URL (Độ phức tạp)
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

// Đếm ký tự đặc biệt trong URL
function countSpecialChars(str) {
    if (!str) return 0;
    const specialChars = str.match(/[^a-zA-Z0-9]/g);
    return specialChars ? specialChars.length : 0;
}

// 2. Hàm tạo khối Placeholder "BLOCKED"
function showBlockedPlaceholder(el) {
    const width = el.offsetWidth || el.width || 300;
    const height = el.offsetHeight || el.height || 250;

    const placeholder = document.createElement('div');
    placeholder.style.width = width + 'px';
    placeholder.style.height = height + 'px';
    placeholder.style.backgroundColor = '#f8d7da'; // Màu đỏ nhạt
    placeholder.style.border = '2px dashed #dc3545'; // Viền đỏ đứt đoạn
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

    // Thay thế phần tử cũ bằng placeholder
    el.parentNode.insertBefore(placeholder, el);
    el.style.display = 'none'; // Ẩn phần tử gốc nhưng vẫn giữ trong DOM để trace
}

// 3. Quét và dự đoán bằng mô hình Advanced
async function scanAndBlock() {
    // Chỉ quét các phần tử dễ là Ads
    const elements = document.querySelectorAll("img, iframe, ins.adsbygoogle, div[id*='ads']");

    for (let el of elements) {
        if (el.dataset.aiChecked) continue;
        el.dataset.aiChecked = "true";

        const url = el.src || el.getAttribute('data-ad-client') || "";

        const features = {
            "dom_depth": getDepth(el),
            "avg_degree_connectivity": getConnectivity(el),
            "num_siblings": el.parentElement ? el.parentElement.children.length - 1 : 0,
            "url_length": url.length,
            "entropy": getEntropy(url),
            "num_special_chars": countSpecialChars(url),
            "is_3rd_party": 1, // Giả định là 3rd party cho demo
            "is_in_iframe": window.self !== window.top ? 1 : 0
        };

       /*         if (url.startsWith('data:image/svg+xml') || url.includes('dantri.com.vn')) {
    return; // Bỏ qua, không scan ảnh hệ thống và ảnh nội bộ
}*/

        try {
            const response = await fetch('http://localhost:8000/predict', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(features)
            });
            const data = await response.json();

            // Sử dụng ngưỡng
            if (data.is_ad) {
                console.log(`🛡️ AI Detected Ads (${(data.probability * 100).toFixed(2)}%):`, url);
                showBlockedPlaceholder(el);
            }
        } catch (e) { console.error("API Error:", e); }
    }
}
// Hàm kiểm tra Third Party thực tế
function isThirdParty(url) {
    try {
        const mailDomain = window.location.hostname.split('.').slice(-2).join('.');
        const adDomain = new URL(url).hostname.split('.').slice(-2).join('.');
        return mailDomain !== adDomain ? 1 : 0;
    } catch (e) { return 0; }
}

// Lắng nghe sự kiện Alt + Click để kiểm tra phần tử
// Dùng mousedown để bắt sự kiện sớm hơn lệnh download của trình duyệt
window.addEventListener('mousedown', async (e) => {
    // Chỉ xử lý nếu nhấn Alt + Chuột trái
    if (e.altKey && e.button === 0) {

        // Tìm phần tử bị click (hoặc thẻ cha nếu là link)
        const el = e.target.closest('img, iframe, a');
        if (!el) return;

        // CHẶN TUYỆT ĐỐI HÀNH ĐỘNG DOWNLOAD/CHUYỂN TRANG
        e.preventDefault();
        e.stopImmediatePropagation();

        // Lấy URL thực tế (ưu tiên ảnh, sau đó đến link)
        const targetEl = e.target.tagName === 'IMG' ? e.target : el;
        const url = targetEl.src || targetEl.href || "";

        console.log("🛡️ [ Inspecting] Target:", url);

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

            // Hiện Alert để demo trong báo cáo môn học
            alert(`--- KẾT QUẢ PHÂN TÍCH AI ---\nDự đoán: ${status}\nXác suất Ads: ${prob}%\n\nĐặc trưng trích xuất:\n- Depth: ${features.dom_depth}\n- Connectivity: ${features.avg_degree_connectivity}\n- Entropy: ${features.entropy.toFixed(2)}`);
        } catch (err) {
            console.error("Lỗi API:", err);
        }
    }
}, true); // Sử dụng Capture mode để chặn sự kiện sớm nhất có thể
// Khởi chạy
scanAndBlock();
setInterval(scanAndBlock, 3000); // Quét lại khi cuộn trang