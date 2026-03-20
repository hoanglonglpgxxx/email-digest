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

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "predict_ad") {
        fetch("http://127.0.0.1:8000/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(request.data)
        })
        .then(res => res.json())
        .then(data => sendResponse({ success: true, data: data }))
        .catch(err => sendResponse({ success: false, error: err.message }));

        return true;
    }
});