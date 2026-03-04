import { InferenceSession, Tensor } from 'onnxruntime-web';

async function predict(features) {
    const session = await InferenceSession.create('./nodeshield_model.onnx');
    const input = new Tensor('float32', Object.values(features), [1, 8]);
    const output = await session.run({ input });
    return output.label.data[0] === 1; // 1 là Ads
}

// Lắng nghe yêu cầu từ background.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === "AI_PREDICT") {
        predict(request.features).then(isAd => sendResponse({ isAd }));
        return true;
    }
});