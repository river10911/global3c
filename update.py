import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz
import re

def fetch_momo_price(url):
    """台灣 momo 價格爬蟲"""
    if "ITEM_CODE" in url: return None # 還是防呆假網址就跳過
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # 嘗試從 momo 網頁的 meta 標籤中精準抓取商品價格
            meta_price = soup.find("meta", property="product:price:amount")
            if meta_price and meta_price.get("content"):
                return int(meta_price["content"])
            
            # 備用方案：尋找網頁上的價格標籤 class
            price_tag = soup.find("span", class_="priceNum")
            if price_tag:
                price_text = re.sub(r'[^\d]', '', price_tag.text)
                return int(price_text)
    except Exception as e:
        print(f"⚠️ 抓取 momo 價格失敗 (可能被阻擋): {e}")
    return None

def fetch_amazon_price(url):
    """日本 Amazon 價格爬蟲 (因 GitHub IP 易被 Amazon 擋，此處做穩健處理)"""
    if "ASIN_CODE" in url: return None
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "ja-JP,ja;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Amazon 價格通常藏在 a-price-whole 這個 class 裡
            price_span = soup.find("span", class_="a-price-whole")
            if price_span:
                price_text = re.sub(r'[^\d]', '', price_span.text)
                return int(price_text)
    except Exception as e:
        print(f"⚠️ 抓取 Amazon 價格失敗 (雲端主機常被 Amazon 驗證碼阻擋): {e}")
    return None

def main():
    # 1. 讀取目前的資料庫
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # 2. 自動更新即時匯率
    print("🔄 正在擷取全球最新即時匯率...")
    fx_url = "https://open.er-api.com/v6/latest/TWD"
    try:
        fx_response = requests.get(fx_url, timeout=10)
        if fx_response.status_code == 200:
            rates = fx_response.json()['rates']
            data['exchangeRates']['JPY'] = round(1 / rates['JPY'], 4)
            data['exchangeRates']['HKD'] = round(1 / rates['HKD'], 4)
            data['exchangeRates']['KRW'] = round(1 / rates['KRW'], 4)
            print("✅ 匯率更新成功！")
    except Exception as e:
        print(f"❌ 匯率 API 連線失敗，沿用舊匯率: {e}")

    # 3. 核心：遍歷各國平台，自動爬取最新價格
    print("🤖 機器人出動，開始巡邏各國電商價格...")
    for region in data['regionsData']:
        platform_name = region['platform']
        
        for capacity, details in region['products'].items():
            product_url = details['link']
            new_price = None
            
            # 根據不同平台執行對應的爬蟲演算法
            if region['id'] == 'tw':
                new_price = fetch_momo_price(product_url)
            elif region['id'] == 'jp':
                new_price = fetch_amazon_price(product_url)
                
            # 【防禦性策略】：只有當真正抓到數字時才覆蓋資料庫，沒抓到就沿用原價，網站絕不崩潰
            if new_price:
                print(f"📈 成功抓取 [{platform_name}] {capacity}GB 最新價格: {new_price}")
                details['price'] = new_price
            else:
                print(f"ℹ️ [{platform_name}] {capacity}GB 未能抓到即時價，保持原紀錄: {details['price']}")

    # 4. 更新時間戳記
    tw_tz = pytz.timezone('Asia/Taipei')
    data['lastUpdated'] = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")

    # 5. 寫回資料庫
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("💾 所有最新資料已封裝存檔！")

if __name__ == "__main__":
    main()
