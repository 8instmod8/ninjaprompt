#!/usr/bin/env bash
set -o errexit

echo "=== Starting build process ==="

pip install -r requirements.txt
python manage.py collectstatic --no-input

echo "=== Running migrations ==="
python manage.py migrate

echo "=== USERS CHECK BEFORE SUPERUSER ==="
python manage.py shell -c "
from django.contrib.auth.models import User
print('Total users:', User.objects.count())
print('Staff users (is_staff=True):', User.objects.filter(is_staff=True).count())
print('Superusers:', User.objects.filter(is_superuser=True).count())
" || true
echo "=== END USERS CHECK ==="

if [ -n "$DJANGO_SUPERUSER_USERNAME" ]; then
    echo "=== Attempting to create superuser ==="
    python manage.py createsuperuser --noinput || true
    echo "=== Superuser creation finished ==="
fi

echo "=== Build completed successfully ==="
