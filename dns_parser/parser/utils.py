# utils.py
import browser_cookie3, undetected_chromedriver as uc

def make_driver(headless: bool = False) -> uc.Chrome:
    """Создаёт uc-Chrome c 'живыми' куками пользователя Chrome."""
    cj = browser_cookie3.chrome(domain_name="dns-shop.ru")

    drv = uc.Chrome(version_main=138, headless=False,
                    options=uc.ChromeOptions())
    drv.get("https://www.dns-shop.ru/")          # любая страница домена
    for c in cj:
        try:
            drv.add_cookie({
                "name": c.name, "value": c.value,
                "domain": c.domain, "path": c.path or "/",
            })
        except Exception:
            pass
    return drv
