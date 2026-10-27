# Прототип внутреннего портала ОГАУЗ «Медсанчасть ИАПО»

Реализация по ТЗ (ред. 11): FastAPI + SQLite + Jinja2. Разделы: главная, поиск,
телефонный справочник, приказы и СОПы с отметками ознакомления, HelpDesk (IT/АХЧ/
Медтехника), нежелательные события, ходатайства и согласование с УКЭП, закупки,
бронирование залов, календарь, объявления, ГО и ЧС, протоколы, сроки, кадры, опросы,
аудиты, формуляр лекарств, МСЭ, учёт активов, новичок, дашборды, уведомления, админка.

## Демо-пользователи (пароль = логин + `123!`, при первом входе — смена пароля)

| Логин | Роль |
|---|---|
| smirnov.av | Администратор системы |
| kozlova.ip | Менеджер качества |
| novikov.sd | Оператор HelpDesk IT |
| fedorova.on | Оператор HelpDesk АХЧ |
| grigoriev.pa | Оператор HelpDesk Медтехника |
| belova.ms | Главный врач |
| kuznetsov.vl | Заместитель главврача |
| rozhdestvenskaya.ti | Заведующая отделением |
| sokolov.do / lebedeva.au | Сотрудники |
| morozova.ev | Отдел кадров |
| volkov.ai | ПЭО |
| zaytseva.np | Подписант УКЭП (гл. бухгалтер) |
| petrov.rs | Регистратор МСЭ |
| sidorova.ma | Аптека |

## Запуск (разработка)

```bash
cd portal
pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
# открыть http://localhost:8000/login
```

База `portal.db` создаётся и наполняется демо-данными автоматически при первом
запуске. Для чистой переинициализации удалите файл `portal.db`.

## Запуск (продакшн)

За смонтированным reverse-proxy (nginx) c несколькими воркерами и systemd:

```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --workers 2 --proxy-headers
```

Примечания:
- SQLite включён в режим WAL — безопасен для нескольких воркеров на одном хосте;
  для кластера из нескольких серверов замените БД на PostgreSQL (схема совместима).
- Секрет сессий задайте переменной окружения `PORTAL_SECRET` (по умолчанию —
  dev-значение).
- HTTPS обязателен по ТЗ (п. нефункциональных требований): терминируйте TLS в nginx
  и добавьте `--proxy-headers --forwarded-allow-ips='*'`.
- Тесты: `python test_portal.py` при запущенном сервере (проверяет все разделы,
  POST-сценарии и разграничение доступа).

## Запуск и тестирование под Windows

### Вариант 1 — PowerShell (рекомендуется)

```powershell
# 1. Установить Python 3.12+ с https://python.org (галка "Add python.exe to PATH")
cd portal
py -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt

# 2. Запуск сервера разработки
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
# открыть http://localhost:8000/login
```

### Вариант 2 — cmd.exe

```bat
cd portal
python -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
python -m uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

### Автоматические тесты (Windows)

В двух окнах PowerShell:

```powershell
# окно 1 — сервер
cd portal; .venv\Scripts\Activate; uvicorn app:app --host 127.0.0.1 --port 8000

# окно 2 — тесты (43 проверки: все разделы, POST-сценарии, роли, блокировка входа)
cd portal; .venv\Scripts\Activate; python test_portal.py
```

Ожидаемый итог: `==== FAILURES: 0`.

### Типичные проблемы на Windows

- **«Access is denied» на pip install** — запускайте терминал без администратора внутри venv, либо `py -m pip install ...`.
- **Порт 8000 занят** (`[Errno 10048]`): смените порт `--port 8080` и в `test_portal.py` строку `BASE = "http://127.0.0.1:8080"`.
- **Антивирус/SmartScreen** блокирует uvicorn — добавьте исключение для папки проекта.
- **Кодировка кириллицы в консоли**: `chcp 65001` перед запуском.
- **Брандмауэр**: для доступа коллег из сети запускайте с `--host 0.0.0.0` и разрешите входящие на порт 8000 (или используйте IIS/nginx как reverse-proxy).
- **Файлы БД** `portal.db-shm/-wal` — служебные SQLite (в .gitignore); для чистой переинициализации удалите `portal.db*`.

### Автозапуск как служба Windows

Проще всего — NSSM: `nssm install PortalMSCh "C:\portal\.venv\Scripts\uvicorn.exe" "app:app --host 127.0.0.1 --port 8000"` (WorkingDirectory = папка portal). Либо планировщик задач с триггером «при загрузке ОС».

### Продакшен под Windows

Uvicorn + IIS ARR (reverse proxy с TLS) или Caddy/nginx for Windows; секрет сессий — `$env:PORTAL_SECRET = "..."` (PowerShell) или `set PORTAL_SECRET=...` (cmd) перед запуском.
