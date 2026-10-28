#!/usr/bin/env bash
# МедПортал: запуск MariaDB (MySQL) + Laravel-сервера
set -e
cd "$(dirname "$0")"

# 1. База данных
if ! mysqladmin ping --silent 2>/dev/null; then
  mkdir -p /run/mysqld && chown mysql:mysql /run/mysqld
  mysqld_safe > /tmp/mysqld.log 2>&1 &
  for i in $(seq 1 30); do mysqladmin ping --silent 2>/dev/null && break; sleep 1; done
fi

# 2. БД и права (создаются один раз, далее идемпотентно)
mysql <<'SQL'
CREATE DATABASE IF NOT EXISTS portal      CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS portal_test CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'portal'@'localhost' IDENTIFIED BY 'portal_pass';
CREATE USER IF NOT EXISTS 'portal'@'127.0.0.1' IDENTIFIED BY 'portal_pass';
GRANT ALL PRIVILEGES ON portal.*      TO 'portal'@'localhost', 'portal'@'127.0.0.1';
GRANT ALL PRIVILEGES ON portal_test.* TO 'portal'@'localhost', 'portal'@'127.0.0.1';
FLUSH PRIVILEGES;
SQL

# 3. Миграции + сиды при пустой базе
TABLES=$(mysql -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='portal';" 2>/dev/null || echo 0)
if [ "$TABLES" -lt 5 ]; then
  php artisan migrate --force
  php artisan db:seed --force
fi

# 4. Веб-сервер
pgrep -f "artisan serve" > /dev/null || (php artisan serve --host=0.0.0.0 --port=8000 > /tmp/serve.log 2>&1 &)
sleep 2
echo "Сайт: http://localhost:8000   (логин: admin@portal.local / password)"
