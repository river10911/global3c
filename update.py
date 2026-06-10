import json
import requests
from datetime import datetime

url = "https://open.er-api.com/v6/latest/USD"

response = requests.get(url, timeout=30)
data = response.json()

exchange = {
"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
"USD": 1,
"TWD": data["rates"]["TWD"],
"JPY": data["rates"]["JPY"],
"HKD": data["rates"]["HKD"],
"KRW": data["rates"]["KRW"]
}

with open("data/exchange.json", "w", encoding="utf-8") as f:
json.dump(
exchange,
f,
ensure_ascii=False,
indent=2
)

print("exchange.json updated")
