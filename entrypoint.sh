#!/bin/bash
set -e

service postgresql start

until psql -U postgres -d postgres -c '\l'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "Postgres is up - continuing"

python manage.py migrate
python manage.py init_data

exec "$@"
