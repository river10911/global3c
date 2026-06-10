import json
from datetime import datetime

with open(
    "data/prices.json",
    "r",
    encoding="utf-8"
) as f:
    prices = json.load(f)

# 模擬抓到的新價格
prices["iphone17"]["amazon_jp"]["price"] = 122800

# 更新時間
prices["_system"] = {
    "last_price_update":
    datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

with open(
    "data/prices.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        prices,
        f,
        ensure_ascii=False,
        indent=2
    )

print("prices.json updated")
