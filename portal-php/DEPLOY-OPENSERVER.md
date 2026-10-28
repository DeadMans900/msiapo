# Установка на OpenServer (Windows) — msiapo2.local

## ⚡ 404 «Не найдено» при открытии http://msiapo2.local/login
Почти всегда это **недостроенный .htaccess** в папке `public` или **не тот корень домена**:
1. Корень домена в OpenServer должен указывать НАПРЯМУЮ на папку `public`:
   `F:\...\domains\msiapo2.local\public`. Если домен создан копированием (перенёсся только index.php, а app/ и vendor/ остались выше) — пересоздайте домен как **ссылку (symlink/junction)** на распакованный проект, либо распакуйте архив целиком внутрь папки домена.
   Быстрая проверка: откройте http://msiapo2.local/index.php — если это работает, а /login даёт 404 → не работает mod_rewrite/.htaccess (см. п.2).
2. В настройках Apache включите `mod_rewrite` (конфиг httpd.conf: `LoadModule rewrite_module`) и для папки проекта:
   `<Directory "..."> AllowOverride All </Directory>` (в OpenServer: конфигурация Apache → снятие комментария с rewrite_module; Alias-домены получают AllowOverride по умолчанию).
3. Файл `public/.htaccess` должен существовать и быть виден (в Windows проводнике включите показ скрытых файлов; некоторые архиваторы/антивирусы его «съедают»). В свежем `msiapo-deploy.zip` он есть.
4. Перезапустите OpenServer после правок.


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
   cd F:\Program\open_server\domains\msiapo2.local
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
   APP_URL=http://msiapo2.local
   ```

5. **Создайте базу** в phpMyAdmin/OpenServer: БД `portal` (utf8mb4_unicode_ci), затем:
   ```powershell
   php artisan migrate:fresh --seed
   ```

6. **Домен в OpenServer**: создайте домен `msiapo2.local` с корнем в папке
   `public` вашего проекта (не самой папки public как docroot-копии — корень
   домена должен указывать на `...\msiapo2.local\public`).

Откройте http://msiapo2.local → вход: admin@portal.local / password

## ⚡ 500 «Внутренняя ошибка сервера» — диагностика за 1 минуту
1. Включите подробный вывод ошибки — в `.env` должно быть:
   ```
   APP_ENV=local
   APP_DEBUG=true
   ```
   затем `php artisan config:clear` и обновите страницу. Laravel покажет точную причину.
2. Типовые причины (по частоте):
   - **Пустой APP_KEY** («No application encryption key…») → `php artisan key:generate`
     (выполняется ОДИН раз после `copy .env.example .env`).
   - **Access denied for user 'root'@'localhost'** → OpenServer по умолчанию пустой пароль root;
     проверьте в `.env`: `DB_USERNAME=root`, `DB_PASSWORD=` (пусто). Если используете
     пользователя `portal` — укажите его пароль.
   - **Base table or view not found … sessions/cache** → сессии/кэш хранились в БД до миграций.
     Актуальный `.env.example` использует `SESSION_DRIVER=file` и `CACHE_STORE=file` —
     перескопируйте `.env` из `.env.example`, затем `php artisan config:clear`.
   - Нет таблиц → `php artisan migrate:fresh --seed`.
3. Точный текст ошибки всегда в `storage/logs/laravel.log` (последная строка ERROR).

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
