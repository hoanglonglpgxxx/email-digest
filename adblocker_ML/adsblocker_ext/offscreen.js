async function predict(features) {
    try {
        // Thay đường dẫn trỏ tới file ONNX chỉ phân tích URL của bạn
        const session = await ort.InferenceSession.create('./nodeshield_url_model.onnx');

        // Căn chỉnh chính xác số lượng features đầu vào
        const inputValues = Float32Array.from(Object.values(features));
        const inputTensor = new ort.Tensor('float32', inputValues, [1, Object.keys(features).length]);

        const feeds = { input: inputTensor }; // Tên input phụ thuộc vào cách bạn export ONNX
        const output = await session.run(feeds);

        return output.label.data[0] === 1n || output.label.data[0] === 1;
    } catch (e) {
        console.error("Lỗi ONNX Predict:", e);
        return false;
    }
}

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "AI_PREDICT") {
        predict(request.features).then(isAd => sendResponse({ isAd }));
        return true; // Bắt buộc return true để giữ cổng kết nối mở cho hàm bất đồng bộ
    }
});