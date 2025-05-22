from flask import Flask, request, jsonify, render_template
import asyncio
from playwright.async_api import async_playwright

import time
import os

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
app = Flask(__name__, template_folder=template_dir)

# In-memory price history storage: {url: [{"timestamp": ..., "price": ..., "platform": ..., "title": ...}, ...]}
price_history_db = {}

async def scrape_amazon_product(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) "
                       "Chrome/114.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded")

        try:
            await page.wait_for_selector("#productTitle", timeout=60000)
        except Exception:
            await browser.close()
            return None, None, None

        title_elem = await page.query_selector("#productTitle")
        title = (await title_elem.inner_text()).strip() if title_elem else None

        price_selectors = [
            "#priceblock_ourprice",
            "#priceblock_dealprice",
            "#priceblock_saleprice",
            ".a-price .a-offscreen"
        ]

        price = None
        for selector in price_selectors:
            price_elem = await page.query_selector(selector)
            if price_elem:
                price = (await price_elem.inner_text()).strip()
                break

        image_elem = await page.query_selector("#imgTagWrapperId img")
        image_url = None
        if image_elem:
            image_url = await image_elem.get_attribute("src")

        await browser.close()
        return title, price, image_url

def parse_price(price_str):
    # Remove currency symbols and commas, convert to float
    if not price_str:
        return None
    price_num = price_str.replace('₹', '').replace(',', '').strip()
    try:
        return float(price_num)
    except:
        return None

def get_other_platform_prices(title):
    # Dummy implementation for other platforms prices
    # In real scenario, scrape or use APIs for other platforms
    platforms = {
        "Flipkart": 13299,
        "Meesho": 13499,
        "BigBasket": None
    }
    return platforms

@app.route('/')
def index():
    return render_template("Index.html")

@app.route('/track', methods=['POST'])
def track():
    data = request.get_json()
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    title, price_str, image_url = asyncio.run(scrape_amazon_product(url))
    if not title or not price_str:
        return jsonify({"error": "Failed to fetch data"}), 500

    price = parse_price(price_str)
    if price is None:
        return jsonify({"error": "Invalid price format"}), 500

    timestamp = int(time.time())

    # Update price history
    history = price_history_db.get(url, [])
    history.append({
        "timestamp": timestamp,
        "price": price,
        "platform": "Amazon",
        "title": title
    })
    price_history_db[url] = history

    # Get other platform prices
    other_platforms = get_other_platform_prices(title)

    # Add other platform prices to history for graph
    for platform, p in other_platforms.items():
        if p is not None:
            history.append({
                "timestamp": timestamp,
                "price": p,
                "platform": platform,
                "title": title
            })

    # Return current data and price history
    return jsonify({
        "title": title,
        "price": price_str,
        "image_url": image_url,
        "price_history": history,
        "other_platforms": other_platforms
    })

if __name__ == '__main__':
    app.run(debug=True)
