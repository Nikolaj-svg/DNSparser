# parser/selenium_uc.py
import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ─── CSS‑селекторы ────────────────────────────────────────────────
CARD_SEL       = "div.catalog-product.ui-button-widget"
SHOW_MORE_SEL  = "button.pagination-widget__show-more-btn"

# ─── основная функция ─────────────────────────────────────────────
def grab_cards(driver,
               url: str,
               click_timeout: int = 10,
               scroll_delay: float = 1.3) -> List[Dict[str, str]]:
    """
    • driver – запущенный uc.Chrome
    • url    – ссылка на категорию DNS
    ↑ возвращает list[{uuid, href}]
    """
    wait = WebDriverWait(driver, 25)
    driver.get(url)

    # ждём первую порцию карточек
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, CARD_SEL)))

    # кликаем «Показать ещё», пока кнопка есть и кликабельна
    while True:
        try:
            btn = WebDriverWait(driver, click_timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SHOW_MORE_SEL))
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(scroll_delay)
        except Exception:
            break   # кнопка исчезла – все товары на странице загружены

    # ── один JS‑вызов → список карточек -------------------------------------------------
    js = """
        return [...document.querySelectorAll(arguments[0])]
               .map(c => {
                   return {
                       uuid: c.dataset.product || "",
                       href: (c.querySelector('a.catalog-product__name') || {}).href || ""
                   };
               });
    """
    cards = driver.execute_script(js, CARD_SEL)
    print(f"🟢 Карточек найдено: {len(cards)}")
    if cards:
        print("▶ first UUID :", cards[0]['uuid'])
        print("▶ first link :", cards[0]['href'])
    return cards
