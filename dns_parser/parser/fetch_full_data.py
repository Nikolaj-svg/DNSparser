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

    chars = []
    for block in data.get("characteristics", {}).values():
        for item in block:
            chars.append(f"{item['title']}: {item['value']}")
    characteristics = "; ".join(chars)

    return {
        "Артикул": data.get("code"),
        "Название": data.get("name") or data.get("title"),
        "Цена": price,
        "Характеристики": characteristics,
        "UUID": uuid,
    }
