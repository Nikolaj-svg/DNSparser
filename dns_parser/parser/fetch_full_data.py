import requests
from typing import Dict

def full_product(uuid: str, cookies: Dict[str, str]) -> dict:
    url = f"https://www.dns-shop.ru/pwa/pwa/get-product/?id={uuid}"
    s   = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    for k, v in cookies.items():
        s.cookies.set(k, v, domain=".dns-shop.ru")

    r = s.get(url, timeout=15)
    if r.status_code != 200:
        print("⚠️ PWA", r.status_code, uuid)
        return {}

    data = r.json().get("data", {})

    raw_price = data.get("price")
    price     = raw_price["value"] if isinstance(raw_price, dict) else raw_price

    # ---------- динамические характеристики ----------
    specs = {}
    chars_data = data.get("characteristics", {})

    if isinstance(chars_data, dict):
        blocks = chars_data.values()
    elif isinstance(chars_data, list):
        blocks = chars_data
    else:
        blocks = []

    for block in blocks:
        if isinstance(block, dict):
            block = [block]
        for item in block:
            title = item.get("title")
            value = item.get("value")
            if title:
                specs[title] = value
    # -------------------------------------------------

    product = {
        "Артикул": data.get("code"),
        "Название": data.get("name") or data.get("title"),
        "Цена": price,
        "Ссылка": "",          # ← placeholder
        "UUID": uuid,
    }
    product.update(specs)
    return product
