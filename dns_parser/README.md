# 🛒 DNS Parser

Парсер товаров с сайта [dns-shop.ru](https://www.dns-shop.ru), собирает:

- **UUID товара**
- **Ссылку на товар**
- **Название**
- **Артикул (Код)**
- **Цену**
- **Характеристики (в одну строку через `;`)**

Все данные сохраняются в `dns_full.xlsx`, по категориям — каждый на отдельный лист.

## 📦 Установка

1. Клонируй репозиторий:

```bash
git clone https://github.com/your-username/dns_parser.git
cd dns_parser
```

2. Создай и активируй виртуальное окружение и зависимости:
```bash
python3 -m venv dns_parser_env
source dns_parser_env/bin/activate
pip install -r requirements.txt
```

3. Запуск:
```bash
python3 main.py
```