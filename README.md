# PythonPlaywright — UI Test Framework for Horilla CRM

Портфолио-проект: фреймворк для UI-автотестов на **Python + Playwright + Pytest** с паттерном **Page Factory** 
и проверками **PostgreSQL**. Тестируемое приложение — **Horilla CRM**, поднимается локально в **Docker**.

## Стек

- **Python 3.13**
- **Playwright** (Chromium/Firefox/WebKit)
- **Pytest** (+ `pytest-xdist`, `pytest-playwright`)
- **Allure** (шаги, скриншоты, видео, trace, SQL)
- **PostgreSQL** + **psycopg2** (проверки БД)
- **Docker** (Horilla CRM)
- **flake8** + **isort** (линтеры)

## Архитектура

Фреймворк построен по слоям:

- **`WebContext`** — инфраструктура (браузер, локаторы, каталог страниц, URL, БД),
- **`Pages`** — текущая страница + прокси методов + HTMX-ожидание,
- **`BasePage`** — действия на странице, проверки, переходы,
- **`BasePagesStore`** — каталог страниц (Page Factory),
- **`Checker`** — проверки БД/сервисов,
- **`PostgreSQLProvider`** — подключение к БД, выполнение SQL,
- **`HorillaQueries`** — SQL-запросы (attach в Allure).

### Ключевые решения

- Локаторы — в YAML (семантика, `**kwargs`, `filter_text`/`filter_not_text`).
- `Pages` — точка входа в тестах (`pages.open_page(...)`, `pages.click(...)`).
- `browser_page` — Playwright `Page` (вкладка), не путать с Page Object.
- HTMX-ожидание после `open_page` (Horilla использует HTMX).
- Проверки БД — через `web_context.horilla_provider` и `web_context.check`.
- SQL-запросы — в `HorillaQueries` (`@staticmethod` + `@attach_source_query` → attach в Allure).

## Тестируемое приложение (Horilla CRM)

| Что | Где |
|---|---|
| **Образ** | `horilla/horilla-crm:latest` ([Docker Hub](https://hub.docker.com/r/horilla/horilla-crm)) |
| **Docker-конфиг** | `config/compose.yaml` |
| **URL** | `http://localhost:8000` |
| **PostgreSQL** | `localhost:5432` (креды в `.env`) |

## Грабли (и как не наступить)

- **Порт PostgreSQL не опубликован** → `docker compose port db 5432` показывает `:0`. Добавь `ports: - "127.0.0.1:5432:5432"` в секцию `db` (`config/compose.yaml`).
- **`WARN: The "w" variable is not set`** → в `SECRET_KEY` (в `.env`) есть `$w`. Экранируй `$` → `$$` **или** заключи значение в **одинарные** кавычки в `.env`.
- **`password authentication failed`** → пароль в `DATABASE_URL` (`compose.yaml`) не совпадает с `POSTGRES_PASSWORD` (`db`). Приведи к одному (из `.env`).
- **`Permission denied: '/app/.init_password'`** → добавь `DB_INIT_PASSWORD` в `environment` сервиса `web` (**или** смонтируй `.init_password` с правами записи).
- **`ERR_CONNECTION_REFUSED` на `localhost:8000`** → контейнер `web` не запущен/упал. Проверь `docker compose logs web`.
- **HTMX: белый экран в Playwright** → после `open_page` жди завершения HTMX-запросов (`.htmx-request, .htmx-settling, .htmx-swapping` → `state="detached"`).
- **`psycopg2: symbol not found '_PQbackendPID'` (M1)** → `pip install psycopg2-binary==2.9.10 --no-cache-dir`.
- **`docker compose` из `horilla-crm/` не видит `ports`** → запускай с `-f ../config/compose.yaml` (**явно** укажи файл).

## Запуск
docker compose -f ../config/compose.yaml up -d
pytest

## Allure
Скриншот — при падении (call/setup),
Видео — записывается, удаляется у успешных тестов, прикрепляется у упавших тестов,
Trace — записывается, прикрепляется у упавших тестов (playwright show-trace trace.zip),
SQL — @attach_source_query прикрепляет тело запроса,
environment.xml — браузер, headless, base URL.

## Проверки БД (SQL + обработка ответов)
Checker + HorillaQueries + horilla_provider

## Переменные окружения (PyCharm)
LOG_LEVEL=DEBUG
ENV=local

## Линтеры
flake8 .
isort .

## Автор
Проект создан как портфолио для демонстрации навыков построения UI-фреймворка с нуля 
(Page Factory, Playwright, Pytest, Allure, Docker, PostgreSQL).
```
