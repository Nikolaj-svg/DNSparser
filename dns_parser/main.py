# main.py
import time, pandas as pd
from tqdm import tqdm
from selenium.common.exceptions import WebDriverException
from parser.utils         import make_driver
from parser.selenium_uc   import grab_cards
from parser.fetch_full_data import full_product

CATEGORY_LINKS = {
    "Процессоры":        "https://www.dns-shop.ru/catalog/17a899cd16404e77/processory/",
    "Материнские платы": "https://www.dns-shop.ru/catalog/17a89a0416404e77/materinskie-platy/",
    "Видеокарты":        "https://www.dns-shop.ru/catalog/17a89aab16404e77/videokarty/",
    "Оперативная память": "https://www.dns-shop.ru/catalog/2d514a593baa7fd7/operativnaya-pamyat/",
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

writer  = pd.ExcelWriter("dns_full.xlsx", engine="openpyxl")
driver  = make_driver(headless=False)        # первый экземпляр

for cat, url in CATEGORY_LINKS.items():
    print(f"\n=== {cat} ===")

    #   ── попытки восстановиться, если окно «умерло» ──
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
    else:
        print("  🔴 Дважды не удалось, пропускаем категорию")
        continue

    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    products = []
    for c in tqdm(cards, desc=cat):
        prod = full_product(c["uuid"], cookies)
        prod["Ссылка"] = c["href"]
        products.append(prod)

    if products:
        pd.DataFrame(products).to_excel(writer, sheet_name=cat[:31], index=False)
        time.sleep(2)

try:
    driver.quit()
except Exception:
    pass

if writer.book.worksheets:
    writer.close()
    print("\n✅ dns_full.xlsx готов")
else:
    print("\n⚠️ Не удалось собрать ни одной категории – Excel не создан")
