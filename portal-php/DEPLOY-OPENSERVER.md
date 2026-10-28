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
- 500 после git-pull → `composer install` + `php artisan config:clear`.
