#!/usr/bin/env bash
set -e

echo "🚀 Деплой Ninja Prompts - $(date)"

cd /var/www/ninjaprompt

git fetch origin
git checkout main
git pull origin main --ff-only

source venv/bin/activate

pip install -r requirements.txt --no-cache-dir

python manage.py migrate --no-input
python manage.py collectstatic --no-input --clear

sudo systemctl restart ninjaprompt

echo "✅ Деплой успешно завершён! $(date)"
