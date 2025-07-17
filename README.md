
# 📦 DNS Parser — Парсер товаров с DNS Shop

Простой и мощный парсер, который собирает данные о товарах с сайта [DNS Shop](https://www.dns-shop.ru) и сохраняет их в Excel-файл.

---

## 🛠️ Поддерживаемые функции

- 📥 Парсинг товаров по категориям
- 🔁 Режим обновления (начинает с последней категории)
- 📦 Сохранение в Excel
- 🖼️ Графический интерфейс (Tkinter)

---

## 📋 Требования

- 🐍 Python 3.9+
- 🖥️ Windows 10/11
- 🌐 Установленный Google Chrome
- 🧭 ChromeDriver (совместимый с версией Chrome)
- 📁 Git (опционально)

---

## 📦 Установка

### 1. Скачайте проект

```bash
git clone https://github.com/Nikolaj-svg/DNSparser.git
cd dns_parser
```

Или же просто скачайте .zip архив с github

### 2. Создайте виртуальное окружение и активируйте его

```bash
python -m venv dns_parser_env
dns_parser_env\Scripts\activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

---

## 🌐 Установка ChromeDriver

### 1. Проверьте версию Google Chrome:
- Откройте Chrome → Нажмите три точки → Справка → О браузере
- Запомните номер версии (например, `120.0.6094.74`)

### 2. Найдите подходящий ChromeDriver:
- Откройте: [https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json](https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json)
- Найди свою версию Chrome, например:
  ```json
  {
    "version": "120.0.6094.74",
    "downloads": {
      "chromedriver": [
        {
          "platform": "win64",
          "url": "https://storage.googleapis.com/chrome-for-testing-public/120.0.6094.74/win64/chromedriver-win64.zip"
        }
      ]
    }
  }
  ```

### 3. Скачайте и распакуйте `chromedriver.exe`:
- Распакуйте архив и поместите `chromedriver.exe` в папку driver
---

## 🚀 Запуск парсера

### Графический интерфейс

```bash
python gui.py
```

> GUI позволяет выбрать режим работы и остановить парсинг с сохранением прогресса.

---

## 📁 Выходной файл

Результаты сохраняются в файл:

```
dns_full.xlsx
```

- Каждая категория — на отдельном листе
- Данные: Артикул, Название, Цена, Характеристики, UUID, Ссылка

---

## ⚠️ Возможные проблемы

| Проблема | Решение |
|---------|---------|
| ChromeDriver не запускается | Проверь, совпадают ли версии Chrome и ChromeDriver |
| GUI не запускается | Убедись, что `tkinter` установлен |
| Ошибка доступа к Excel | Не открывай файл во время парсинга |
| Антивирус блокирует ChromeDriver | Добавь папку проекта в исключения |
| Появляются дубли товаров | Убедись, что `uuid` сохраняется корректно |

---

## 💡 Советы


- 📁 Сохраняй резервные копии `dns_full.xlsx` перед большими сессиями парсинга

- 🕒 Можно запускать парсер в фоне и не закрывать окно хрома.

---

## 📁 Структура проекта

```
dns_parser/
│
├── main.py                # Основной парсер
├── gui.py                 # Графический интерфейс
├── requirements.txt       # Зависимости
├── dns_full.xlsx          # Выходной файл
│
└── parser/
    ├── selenium_uc.py     # Парсинг карточек
    ├── fetch_full_data.py # Парсинг данных по товарам
    └── utils.py           # Утилиты (например, создание драйвера)
```

---