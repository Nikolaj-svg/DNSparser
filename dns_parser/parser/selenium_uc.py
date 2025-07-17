# parser/selenium_uc.py

import time
from typing import List, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ─── CSS‑селекторы ────────────────────────────────────────────────
CARD_SEL = "div.catalog-product.ui-button-widget"
SHOW_MORE_SEL = "button.pagination-widget__show-more-btn"
ITEM_COUNT_SEL = "span.products-count"  # селектор для счётчика товаров

# ─── Константы ────────────────────────────────────────────────────
ITEMS_PER_PAGE = 18  # товаров на странице
CARDS_PER_BATCH = 10  # кликов «Показать ещё» за один подход


def get_total_items(driver) -> int:
    """
    Получает общее количество товаров в категории.
    ↑ возвращает int или None
    """
    try:
        count_el = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ITEM_COUNT_SEL))
        )
        text = count_el.text.strip()
        if text:
            return int(text.split()[0])
    except Exception as e:
        print("❌ Не удалось получить количество товаров:", e)
    return 0


def click_show_more(driver, max_clicks: int = 18, scroll_delay: float = 1.3) -> List[Dict[str, str]]:
    """
    Кликает по кнопке «Показать ещё» заданное количество раз.
    ↑ возвращает список карточек
    """
    cards = []

    for i in range(max_clicks):
        try:
            btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, SHOW_MORE_SEL))
            )
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(scroll_delay)

            # Получаем текущее количество карточек
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
            print(f"📦 Загружено карточек: {len(cards)} (клик {i + 1})")

        except TimeoutException:
            print("🛑 Больше товаров нет или кнопка не найдена.")
            break

    return cards


def grab_cards(driver, base_url: str, total_items: int, scroll_delay: float = 1.3) -> List[Dict[str, str]]:
    """
    Гибридный метод:
    - Каждые 10 кликов «Показать ещё» → переход на ?p=XX и повтор
    - Позволяет обойти перегрузку DOM
    ↑ возвращает list[{uuid, href}]
    """
    total_pages = (total_items // ITEMS_PER_PAGE) + (1 if total_items % ITEMS_PER_PAGE != 0 else 0)
    print(f"📖 Всего страниц в категории: {total_pages}")

    all_cards = []
    start_page = 1

    for batch_num in range(0, total_pages, CARDS_PER_BATCH):
        page = start_page + batch_num
        print(f"\n🔄 Блок {batch_num // CARDS_PER_BATCH + 1}: Страница {page}–{page + CARDS_PER_BATCH - 1}")

        # Переход на страницу
        page_url = f"{base_url}&p={page}" if page > 1 else base_url
        print(f"🧭 Переходим на: {page_url}")
        driver.get(page_url)

        # Ждём загрузки карточек
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, CARD_SEL))
            )
        except TimeoutException:
            print("❌ Не удалось загрузить карточки на странице")
            continue

        # Кликаем «Показать ещё» до CARDS_PER_BATCH раз
        print(f"🖱️ Кликаем 'Показать ещё' до {CARDS_PER_BATCH} раз")
        cards = click_show_more(driver, max_clicks=CARDS_PER_BATCH, scroll_delay=scroll_delay)

        # Сохраняем
        all_cards.extend(cards)
        print(f"✅ В этом блоке собрано карточек: {len(cards)}")

        # Проверяем, не вышли ли за лимит страниц
        if page + CARDS_PER_BATCH > total_pages:
            break

    print(f"\n✅ Общее количество карточек: {len(all_cards)}")
    return all_cards