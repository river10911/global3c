import json

with open(
    "data/prices.json",
    "r",
    encoding="utf-8"
) as f:
    prices = json.load(f)

prices["iphone17"]["amazon_jp"]["price"] = 123456

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
