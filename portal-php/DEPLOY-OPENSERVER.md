# Установка на OpenServer (Windows) — msiapo.test

Ошибка `require(.../vendor/autoload.php): No such file or directory` означает,
что не установлены PHP-зависимости: папка `vendor/` намеренно исключена из Git
(.gitignore), её нужно собрать на своей машине.

## Шаги

1. **Установите Composer** (однократно):
   ```powershell
   winget install Composer.Composer
   ```
   или скачайте с https://getcomposer.org/download/

2. **Проверьте версию PHP в OpenServer**: Module → PHP → включите PHP 8.2 или 8.3.
   В `.ini` должны быть активны расширения: `pdo_mysql`, `mbstring`, `openssl`,
   `fileinfo`, `curl`, `zip` (в OpenServer включаются галочками в настройках PHP).

3. **Установите зависимости** (в корне проекта, там где composer.json):
   ```powershell
   cd F:\Program\open_server\domains\msiapo.test
   composer install --no-dev --optimize-autoloader
   ```

4. **Создайте .env**:
   ```powershell
   copy .env.example .env
   php artisan key:generate
   ```
   В `.env` укажите доступ к MySQL OpenServer:
   ```
   DB_CONNECTION=mysql
   DB_HOST=127.0.0.1
   DB_PORT=3306
   DB_DATABASE=portal
   DB_USERNAME=root
   DB_PASSWORD=
   APP_URL=http://msiapo.test
   ```

5. **Создайте базу** в phpMyAdmin/OpenServer: БД `portal` (utf8mb4_unicode_ci), затем:
   ```powershell
   php artisan migrate:fresh --seed
   ```

6. **Домен в OpenServer**: создайте домен `msiapo.test` с корнем в папке
   `public` вашего проекта (не самой папки public как docroot-копии — корень
   домена должен указывать на `...\msiapo.test\public`).

Откройте http://msiapo.test → вход: admin@portal.local / password

## Частые проблемы
- Нет `php` в PATH → используйте консоль OpenServer («Консоль» → PowerShell от админа)
  или полный путь: `F:\Program\open_server\userdata\php\php-8.2-nts-Win32-VS17-x64\php.exe artisan ...`
- `could not find driver` → выключено `pdo_mysql` в настройках PHP модуля OpenServer.
- **500 «Внутренняя ошибка сервера»** — самые частые причины по порядку:
  1. `.env` скопирован из старого `.env.example`, где было `DB_CONNECTION=sqlite`
     и закомментированы `DB_HOST/DB_PORT/DB_DATABASE/DB_USERNAME/DB_PASSWORD`
     → Laravel падает при подключении к БД. В актуальном `.env.example` (в репозитории)
     уже прописан mysql — просто перескопируйте: `copy .env.example .env`
     (не забудьте затем `php artisan key:generate`).
  2. Не создан ключ APP_KEY → `php artisan key:generate`.
  3. Не выполнены миграции (нет таблиц) → `php artisan migrate:fresh --seed`.
  4. Старый кэш конфигурации → `php artisan config:clear && php artisan cache:clear`.
  5. Недоступны права на запись в `storage/` (редко на Windows).
  Точный текст ошибки смотрите в логе: `storage/logs/laravel.log` (последняя строка ERROR)
  или временно поставьте в `.env`: `APP_DEBUG=true` и `APP_ENV=local`.
- Composer требует PHP ≥8.2: убедитесь, что именно версия из OpenServer вызывается
  командой `php -v` (в консоли OpenServer это по умолчанию так).
