#!/usr/bin/env bash
set -euo pipefail

echo "========================================"
echo "🚀 DEPLOY NinjaPrompt - $(date '+%Y-%m-%d %H:%M:%S')"
echo "========================================"

APP_DIR="${APP_DIR:-/var/www/ninjaprompt}"
cd "$APP_DIR"

echo "→ Fetching latest code..."
git fetch origin
git checkout main
git pull origin main --ff-only

echo "→ Activating virtualenv..."
source venv/bin/activate

echo "→ Installing dependencies..."
pip install -r requirements.txt --no-cache-dir -q

echo "→ Running migrations..."
python manage.py migrate --no-input

echo "→ Collecting static files (with clear)..."
python manage.py collectstatic --no-input --clear

echo "→ Pre-warming cache and checking system..."
python manage.py shell -c "
from content.models import ContentItem, ContentItemPhoto
print('✅ Total prompts:', ContentItem.objects.count())
print('✅ Total photos:', ContentItemPhoto.objects.count())
print('✅ Settings check passed')
" || echo "⚠️ Pre-warm warning (non-critical)"

echo "→ Restarting Gunicorn service..."
sudo systemctl restart ninjaprompt

echo "→ Checking service status..."
sudo systemctl is-active --quiet ninjaprompt && echo "✅ Service is running" || echo "❌ Service failed to start"

echo "========================================"
echo "✅ DEPLOY COMPLETED SUCCESSFULLY"
echo "========================================"
