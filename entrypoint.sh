#!/bin/sh
set -e

echo "Waiting for PostgreSQL to accept connections on $POSTGRES_HOST:$POSTGRES_PORT..."
RETRIES=5
COUNT=0
until pg_isready -h db -U "$POSTGRES_USER" -t 30 || [ $COUNT -eq $RETRIES ]; do
    echo "Waiting for database... ($COUNT/$RETRIES)"
    COUNT=$((COUNT+1))
    sleep 5
done

if [ $COUNT -eq $RETRIES ]; then
    echo "Error: Failed to connect to database after $RETRIES attempts"
    exit 1
fi

echo "Creating migrations..."
export PGPASSWORD=$POSTGRES_PASSWORD
psql -h db -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c 'CREATE EXTENSION IF NOT EXISTS vector;'
python manage.py makemigrations documents

echo "Applying database migrations..."
until python manage.py migrate --noinput; do
  echo "Migrations failed, retrying in 5 seconds..."
  sleep 5
done

echo "Starting server..."
# Execute the passed command (Django server or Celery worker)
exec "$@"
