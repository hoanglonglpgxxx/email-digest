import * as orb from 'onnxruntime-web';

chrome.runtime.onMessage.addListener(async (msg, sender, sendResponse) => {
    if (msg.type === "AI_PREDICT") {
        try {
            const session = await orb.InferenceSession.create('./model.onnx');
            const input = new orb.Tensor('float32', Object.values(msg.features), [1, Object.keys(msg.features).length]);
            const output = await session.run({ input: input });
            const isAd = output.label.data[0] === 1;
            sendResponse({ isAd });
        } catch (e) {
            sendResponse({ isAd: false });
        }
    }
    return true;
});