const getDepth = el => {
    let depth = 0;
    while (el.parentNode) { el = el.parentNode; depth++; }
    return depth;
};

const getConnectivity = el => {
    let siblings = el.parentElement ? el.parentElement.children.length - 1 : 0;
    let children = el.children.length;
    return 1 + siblings + children;
};

const getEntropy = str => {
    if (!str) return 0;
    const freq = {};
    for (let char of str) freq[char] = (freq[char] || 0) + 1;
    return Object.values(freq).reduce((acc, f) => {
        let p = f / str.length;
        return acc - p * Math.log2(p);
    }, 0);
};

const isThirdParty = url => {
    try {
        const main = window.location.hostname.split('.').slice(-2).join('.');
        const req = new URL(url).hostname.split('.').slice(-2).join('.');
        return main !== req ? 1 : 0;
    } catch { return 0; }
};

const countSpecialChars = url => {
    if (!url) return 0;
    return (url.match(/[^a-zA-Z0-9]/g) || []).length;
};

function getEffectiveUrl(el) {
    let url = el.src || el.href || "";
    if (el.tagName === 'IMG') {
        const parentLink = el.closest('a');
        if (parentLink && parentLink.href) {
            url = parentLink.href;
        }
    }
    return url;
}

const isInsideIframe = (el) => {
    return (el.tagName === 'IFRAME' || el.closest('iframe') !== null || window.self !== window.top) ? 1 : 0;
};

window.addEventListener('click', (e) => {
    if (e.altKey) {
        e.preventDefault();
        e.stopPropagation();
        e.stopImmediatePropagation();

        const el = e.target.closest('img, iframe, a, script');
        if (!el) return;

        const url = getEffectiveUrl(el);

        const features = {
            "is_3rd_party": isThirdParty(url),
            "url_length": url.length,
            "entropy": getEntropy(url),
            "num_special_chars": countSpecialChars(url),
            "dom_depth": getDepth(el),
            "num_siblings": el.parentElement ? el.parentElement.children.length - 1 : 0,
            "avg_degree_connectivity": getConnectivity(el),
            "is_in_iframe": isInsideIframe(el),
            "structure_density": (el.parentElement ? el.parentElement.children.length - 1 : 0) / (getDepth(el) + 1),
            "url_complexity": countSpecialChars(url) / (url.length + 1)
        };

        chrome.runtime.sendMessage({ action: "predict_ad", data: features }, (response) => {
            if (response?.success) {
                const status = response.data.is_ad ? "QUẢNG CÁO" : "SẠCH";
                alert(`\nKết quả: ${status}\nXác suất: ${(response.data.probability * 100).toFixed(2)}%\nURL xử lý: ${url.substring(0, 50)}...`);
            } else {
                alert("Lỗi kết nối Server AI Local!");
            }
        });
    }
}, true);

function analyzeElement(el) {
    const url = getEffectiveUrl(el);
    if (!url || url.startsWith("data:")) return;

    const features = {
        "is_3rd_party": isThirdParty(url),
        "url_length": url.length,
        "entropy": getEntropy(url),
        "num_special_chars": countSpecialChars(url),
        "dom_depth": getDepth(el),
        "num_siblings": el.parentElement ? el.parentElement.children.length - 1 : 0,
        "avg_degree_connectivity": getConnectivity(el),
        "is_in_iframe": isInsideIframe(el),
        "structure_density": (el.parentElement ? el.parentElement.children.length - 1 : 0) / (getDepth(el) + 1),
        "url_complexity": countSpecialChars(url) / (url.length + 1)
    };

    chrome.runtime.sendMessage({ action: "predict_ad", data: features }, (response) => {
        if (response?.success) {
            if (response.data.is_ad) {
                console.log(`[BỊ CHẶN] Quảng cáo: ${url.substring(0, 50)}...`);

                const targetToBlock = el.closest('.dta-unit, .mdbl, [id*="google_ads"], .ads-banner, ins') || el;

                // Lấy kích thước thực tế của khối quảng cáo trước khi xóa
                const rect = targetToBlock.getBoundingClientRect();
                const currentWidth = rect.width > 0 ? rect.width + 'px' : '100%';
                const currentHeight = rect.height > 0 ? rect.height + 'px' : '100%';

                // Đảm bảo thẻ cha có position relative cho khối absolute
                const computedStyle = window.getComputedStyle(targetToBlock);
                if (computedStyle.position === 'static') {
                    targetToBlock.style.setProperty('position', 'relative', 'important');
                }

                // Giữ nguyên kích thước container để không làm vỡ layout
                targetToBlock.style.setProperty('min-width', currentWidth, 'important');
                targetToBlock.style.setProperty('min-height', currentHeight, 'important');

                targetToBlock.innerHTML = '';

                const overlay = document.createElement('div');
                overlay.style.cssText = `
                    position: absolute !important;
                    top: 0 !important;
                    left: 0 !important;
                    width: 100% !important;
                    height: 100% !important;
                    background-color: #fff5f5 !important;
                    border: 2px dashed red !important;
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    z-index: 2147483647 !important;
                    box-sizing: border-box !important;
                    pointer-events: none !important;
                `;
                overlay.innerHTML = '<span style="color: red; font-weight: bold; font-size: 14px; font-family: sans-serif; letter-spacing: 1px;">BLOCKED</span>';

                targetToBlock.appendChild(overlay);
            }
        }
    });
}

const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
        mutation.addedNodes.forEach((node) => {
            if (node.tagName === 'IMG' || node.tagName === 'IFRAME') {
                analyzeElement(node);
            } else if (node.querySelectorAll) {
                node.querySelectorAll('img, iframe').forEach(analyzeElement);
            }
        });
    });
});
observer.observe(document.body, { childList: true, subtree: true });