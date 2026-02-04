import asyncio
from playwright.async_api import async_playwright
import pandas as pd
from urllib.parse import urlparse
import os


async def crawl_on_local(site_url):
    ads_found = []
    target_path = f"{site_url.rstrip('/')}/phimhay"

    async with async_playwright() as p:
        # headless=False giúp bạn quan sát Cloudflare giải đố
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        # Tiêm mã giả lập người dùng (Stealth)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', {get: () => ['vi-VN', 'vi', 'en-US', 'en']});
        """)

        print(f"-> Đang mở trình duyệt: {target_path}")
        try:
            # Dùng domcontentloaded để nhanh hơn và tránh treo
            await page.goto(target_path, wait_until="domcontentloaded", timeout=60000)

            # Đợi Cloudflare tự giải (Thường IP nhà sẽ qua ngay)
            print("-> Chờ 15s để trang load Ads và giải Cloudflare...")
            await asyncio.sleep(15)

            title = await page.title()
            print(f"-> Tiêu đề trang: {title}")

            # Cuộn trang để kích hoạt Lazy Load cho các banner
            await page.mouse.wheel(0, 1000)
            await asyncio.sleep(2)

            # Quét các thẻ Ads cá cược class 'is-image'
            ad_elements = await page.query_selector_all("a.is-image")
            print(f"-> Tìm thấy {len(ad_elements)} mẫu Ads tiềm năng.")

            for a in ad_elements:
                href = await a.get_attribute('href')
                img = await a.query_selector('img')
                src = await img.get_attribute('src') if img else None

                # Chỉ lấy link dẫn ra ngoài (Third-party) để làm nhãn 1
                if href and src and "rophim" not in href:
                    ads_found.append({
                        "url": src,
                        "target_url": href,
                        "is_ad": 1
                    })
                    print(f"🔥 Bắt được Ads: {urlparse(href).netloc}")

        except Exception as e:
            print(f"-> Lỗi: {e}")
        finally:
            await browser.close()
    return ads_found


if __name__ == "__main__":
    url = "https://rophim.la/"
    data = asyncio.run(crawl_on_local(url))

    if data:
        df = pd.DataFrame(data)
        file_name = "bet_ads_raw.csv"
        # Nối tiếp vào file cũ nếu đã tồn tại
        file_exists = os.path.isfile(file_name)
        df.to_csv(file_name, mode='a', index=False, header=not file_exists)
        print(f"-> Đã lưu thêm {len(df)} mẫu Ads vào {file_name}")
    else:
        print("-> Không thu thập được mẫu nào. Hãy thử click vào trang thủ công trước.")