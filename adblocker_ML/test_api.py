import requests

api_url = "http://localhost:8000/check-link"

# Danh sách link muốn test
links_to_test = [
    # 1. Link quảng cáo thật (Banner Google)
    "https://tpc.googlesyndication.com/simgad/11738263884841964264",

    # 2. Link ảnh tin tức bình thường (VnExpress)
    "https://vcdn1-vnexpress.vnecdn.net/2024/02/02/du-lich-tet-1-1706846152.jpg",

    # 3. Link chết hoặc không tải được (Để test khả năng xử lý lỗi)
    "https://example.com/khong-ton-tai.jpg"
]

for link in links_to_test:
    print(f"\n--- Đang check: {link} ---")
    try:
        # Gửi đúng 1 trường "url" duy nhất
        resp = requests.post(api_url, json={"url": link})
        print("KẾT QUẢ:", resp.json())
    except Exception as e:
        print("Lỗi kết nối:", e)