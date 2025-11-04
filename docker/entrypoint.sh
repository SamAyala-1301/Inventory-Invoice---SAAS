#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\q'; do
  echo "Postgres is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing migrations"
python manage.py migrate --noinput || echo "Migrations failed but continuing..."

echo "Starting server..."
exec "$@"