#!/usr/bin/env bash
set -o errexit

echo "=== Starting build process ==="
pip install -r requirements.txt
python manage.py collectstatic --no-input
echo "=== Running migrations ==="
python manage.py migrate

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "=== Attempting to create superuser ==="
    python manage.py createsuperuser --noinput || true
    echo "=== Superuser creation finished ==="
fi
echo "=== Build completed successfully ==="
