import json
import requests
from datetime import datetime
import pytz

def update_exchange_rates():
    # 1. 讀取現有的 data.json
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print("找不到 data.json 檔案")
        return

    # 2. 透過免費 API 抓取最新匯率 (基準為 USD，我們自行換算)
    url = "https://open.er-api.com/v6/latest/TWD"
    try:
        response = requests.get(url)
        response.raise_for_status()
        api_data = response.json()
        rates = api_data['rates']
        
        # 3. 更新我們 JSON 裡的匯率數字 (四捨五入到小數點後四位)
        data['exchangeRates']['JPY'] = round(1 / rates['JPY'], 4)
        data['exchangeRates']['HKD'] = round(1 / rates['HKD'], 4)
        data['exchangeRates']['KRW'] = round(1 / rates['KRW'], 4)
        
        # 4. 更新最後抓取的時間 (設定為台灣時間)
        tw_tz = pytz.timezone('Asia/Taipei')
        tw_time = datetime.now(tw_tz).strftime("%Y-%m-%d %H:%M:%S")
        data['lastUpdated'] = tw_time
        
        # 5. 把新數字存回 data.json
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        print(f"✅ 匯率更新成功！時間：{tw_time}")
        
    except Exception as e:
        print(f"❌ 更新失敗：{e}")

if __name__ == "__main__":
    update_exchange_rates()
