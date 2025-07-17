# main.py

import time
import os
import json
import pandas as pd
from tqdm import tqdm
from selenium.common.exceptions import WebDriverException
from parser.utils import make_driver
from parser.selenium_uc import grab_cards, get_total_items
from parser.fetch_full_data import full_product

CATEGORY_LINKS = {
    "Процессоры":        "https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/",
    "Материнские платы": "https://www.dns-shop.ru/catalog/17a89a0416404e77/materinskie-platy/",
    "Видеокарты":        "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/",
    "Оперативная память dimm" : "https://www.dns-shop.ru/catalog/17a89a3916404e77/operativnaya-pamyat-dimm/",
    "Оперативная память SO-DIMM" : "https://www.dns-shop.ru/catalog/17a9b91b16404e77/operativnaya-pamyat-so-dimm/",
    "Блоки питания": "https://www.dns-shop.ru/catalog/17a89c2216404e77/bloki-pitaniya/",
    "Корпуса": "https://www.dns-shop.ru/catalog/17a89c5616404e77/korpusa/",
    "Кулеры для процессоров": "https://www.dns-shop.ru/catalog/17a9cc2d16404e77/kulery-dlya-processorov/",
    "СЖО": "https://www.dns-shop.ru/catalog/17a9cc9816404e77/sistemy-zhidkostnogo-ohlazhdeniya/",
    "Вентиляторы для корпуса": "https://www.dns-shop.ru/catalog/17a9cf0216404e77/ventilyatory-dlya-korpusa/",
    "Термоинтерфейсы": "https://www.dns-shop.ru/catalog/17a9cccc16404e77/termointerfejsy/",
    "Водоблоки": "https://www.dns-shop.ru/catalog/46a6ee18ae77e78a/vodobloki/",
    "Радиаторы СЖО": "https://www.dns-shop.ru/catalog/c337d10545a1d894/radiatory-szho/",
    "Помпы СЖО": "https://www.dns-shop.ru/catalog/2cacbd38aaea1804/pompy-szho/",
    "Трубки и шланги": "https://www.dns-shop.ru/catalog/36ca7a16b10e23fd/trubki-i-shlangi/",
    "Фитинги для СЖО": "https://www.dns-shop.ru/catalog/7dd2f94fbd40b838/fitingi-dlya-szho/",
    "Жидкость для охлаждения": "https://www.dns-shop.ru/catalog/d9afd9ed4713ecfd/zhidkost-dlya-oxlazhdeniya/",
    "Бэкплейты для видеокарт": "https://www.dns-shop.ru/catalog/ba01d15ff8c9184b/bekplejty-dlya-videokart/",
    "Термопрокладки": "https://www.dns-shop.ru/catalog/85fe8b0e83901664/termoprokladki/",
    "Радиаторы для памяти": "https://www.dns-shop.ru/catalog/17a89a6e16404e77/radiatory-dlya-pamyati/",
    "Радиаторы для SSD M.2": "https://www.dns-shop.ru/catalog/17a9cfd716404e77/radiatory-dlya-ssd-m2/",
    "Термоклей": "https://www.dns-shop.ru/catalog/17a9cd3616404e77/termoklej/",
    "SSD накопители": "https://www.dns-shop.ru/catalog/8a9ddfba20724e77/ssd-nakopiteli/",
    "SSD M.2 накопители": "https://www.dns-shop.ru/catalog/dd58148920724e77/ssd-m2-nakopiteli/",
    "Адаптеры для накопителей": "https://www.dns-shop.ru/catalog/ed60465eacbf3c59/adaptery-dlya-nakopitelej/",
    "Серверные SSD": "https://www.dns-shop.ru/catalog/recipe/4fef73f9c0e09a2c/servernye-ssd/",
    "Док-станции для накопителей": "https://www.dns-shop.ru/catalog/17a9d1c016404e77/dok-stancii-dlya-nakopitelej/",
    "Внешние боксы для накопителей": "https://www.dns-shop.ru/catalog/17a9d18916404e77/vneshnie-boksy-dlya-nakopitelej/",
    "Серверные SSD M.2": "https://www.dns-shop.ru/catalog/recipe/5bb555d805b6001e/servernye-ssd-m2/",
    "HDD 3.5": "https://www.dns-shop.ru/catalog/17a8914916404e77/zhestkie-diski-35/",
    "HDD 2.5": "https://www.dns-shop.ru/catalog/f09d15560cdd4e77/zhestkie-diski-25/",
    "Серверные HDD": "https://www.dns-shop.ru/catalog/17aa4e3216404e77/servernye-hdd/",
    "Мониторы": "https://www.dns-shop.ru/catalog/17a8943716404e77/monitory/?virtual_category_uid=49bf328b84625c82"

}

FILENAME = "dns_full.xlsx"
STATE_FILE = "parser_state.json"

def load_existing_uuids(filename, category):
    """
    Загружает все uuid из Excel для указанной категории.
    ↑ возвращает множество uuid
    """
    if not os.path.exists(filename):
        return set()

    try:
        with pd.ExcelFile(filename) as xls:
            sheet_name = category[:31]
            if sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name)
                if not df.empty and 'uuid' in df.columns:
                    return set(df['uuid'].astype(str).str.strip())
    except Exception as e:
        print(f"⚠️ Не удалось загрузить uuid из {category}: {e}")
    return set()

def load_last_uuids(filename):
    if not os.path.exists(filename):
        return {}

    last_uuids = {}
    with pd.ExcelFile(filename) as xls:
        for sheet in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet)
            if not df.empty and 'uuid' in df.columns:
                last_uuids[sheet] = df.iloc[-1]['uuid']
    return last_uuids


def save_partial(category, products):
    if not products:
        return

    mode = 'a' if os.path.exists(FILENAME) else 'w'
    with pd.ExcelWriter(FILENAME, engine='openpyxl', mode=mode) as writer:
        pd.DataFrame(products).to_excel(writer, sheet_name=category[:31], index=False)


def save_state(current_state):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(current_state, f, indent=2)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    with open(STATE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def run(mode="update", is_running=lambda: True):
    driver = make_driver(headless=False)
    last_uuids = load_last_uuids(FILENAME) if mode == "update" else {}
    current_state = load_state() if mode == "update" else {}

    try:
        for cat, url in CATEGORY_LINKS.items():
            if not is_running():
                print("⛔ Парсинг остановлен пользователем.")
                break

            print(f"\n=== {cat} ===")

            # Заходим на страницу и получаем общее число товаров
            driver.get(url)
            total_items = get_total_items(driver)
            print(f"📦 Всего товаров на сайте: {total_items}")

            # Проверяем, есть ли данные в Excel
            if os.path.exists(FILENAME):
                try:
                    df = pd.read_excel(FILENAME, sheet_name=cat[:31])
                    if not df.empty:
                        excel_count = len(df)
                        print(f"💾 Товаров в Excel: {excel_count}")
                        if excel_count >= total_items:
                            print("✅ Категория уже полностью загружена. Пропускаем.")
                            continue
                except Exception as e:
                    print(f"⚠️ Не удалось прочитать лист {cat}: {e}")

            products = []

            # Получаем карточки
            cards = []
            for attempt in (1, 2):
                try:
                    cards = grab_cards(driver, url)
                    break
                except WebDriverException as e:
                    print(f"  ⛔ Selenium error (try {attempt}): {e.msg[:90]}…")
                    try:
                        driver.quit()
                    except Exception:
                        pass
                    driver = make_driver(headless=False)

            if not cards:
                print("⛔ Не удалось получить карточки для этой категории.")
                continue

            cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

            # Пропускаем уже собранные товары
            last_uuid = last_uuids.get(cat, None)
            existing_uuids = load_existing_uuids(FILENAME, cat)
            skip = True if last_uuid else False

            for c in tqdm(cards, desc=cat):
                if not is_running():
                    print("⛔ Парсинг остановлен пользователем.")
                    save_partial(cat, products)
                    save_state(current_state)
                    driver.quit()
                    return

                if skip:
                    if c["uuid"] == last_uuid:
                        skip = False
                    continue
                # Пропускаем товар, если он уже есть в Excel
                if c["uuid"] in existing_uuids:
                    print(f"🔁 Товар {c['uuid']} уже есть в Excel. Пропускаем.")
                    continue

                prod = full_product(c["uuid"], cookies)
                prod["uuid"] = c["uuid"]
                prod["Ссылка"] = c["href"]
                products.append(prod)
                current_state['last_processed'] = {"category": cat, "uuid": c["uuid"]}

            # Сохраняем после каждой категории
            save_partial(cat, products)
            products = []
            time.sleep(1)

    except Exception as e:
        print("❌ Ошибка во время парсинга:", e)
    finally:
        try:
            driver.quit()
        except Exception:
            pass
        print("\n✅ dns_full.xlsx готов")