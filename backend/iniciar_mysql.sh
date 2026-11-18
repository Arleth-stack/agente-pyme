#!/bin/sh
# Arranca el MySQL local SOLO de este proyecto (puerto 3307, datos en backend/.mysql-local).
# No usa el MySQL del sistema ni pide contraseña de administrador.
cd "$(dirname "$0")"
if [ -f .mysql-local/mysqld.pid ] && kill -0 "$(cat .mysql-local/mysqld.pid)" 2>/dev/null; then
  echo "MySQL local ya está corriendo (puerto 3307)."; exit 0
fi
/usr/local/mysql/bin/mysqld --defaults-file="$PWD/.mysql-local/my.cnf" --daemonize >/dev/null 2>&1 \
  || /usr/local/mysql/bin/mysqld --defaults-file="$PWD/.mysql-local/my.cnf" &
sleep 3
echo "MySQL local listo en 127.0.0.1:3307"
