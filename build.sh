#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "🔨 BUILD NinjaPrompt - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

echo "→ Installing Python dependencies..."
pip install -r requirements.txt --no-cache-dir -q

echo "→ Running database migrations..."
python manage.py migrate --no-input

echo "→ Collecting static files..."
python manage.py collectstatic --no-input --clear

echo "→ Pre-warming cache..."
python manage.py shell -c "
from content.models import ContentItem
print('✅ Total prompts in DB:', ContentItem.objects.count())
" || true

if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
    echo "→ Creating superuser (if not exists)..."
    python manage.py createsuperuser --noinput || true
fi

echo "========================================"
echo "✅ BUILD COMPLETED SUCCESSFULLY"
echo "========================================"
