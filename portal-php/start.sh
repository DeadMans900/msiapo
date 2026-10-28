#!/usr/bin/env bash
# Запуск МедПортала: MariaDB + Laravel (php artisan serve)
set -e
cd "$(dirname "$0")"
if ! mysqladmin ping --silent 2>/dev/null; then
  mkdir -p /run/mysqld && chown mysql:mysql /run/mysqld
  mysqld_safe > /tmp/mysqld.log 2>&1 &
  for i in $(seq 1 30); do mysqladmin ping --silent 2>/dev/null && break; sleep 1; done
fi
pgrep -f "artisan serve" > /dev/null || (php artisan serve --host=0.0.0.0 --port=8000 > /tmp/serve.log 2>&1 &)
echo "Сайт: http://localhost:8000  (логин: admin@portal.local / password)"
