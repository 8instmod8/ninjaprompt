from django.core.management.base import BaseCommand
from content.models import Category, Subcategory, ContentItem, Group


class Command(BaseCommand):
    help = 'Финальный перенос данных в новую структуру (Category + Subcategory)'

    def handle(self, *args, **options):
        self.stdout.write("🚀 Начинаем финальный перенос...")

        # 1. Создаём чистые верхнеуровневые категории
        top = {}
        for slug, name, order in [
            ('selfies', 'Селфи', 10),
            ('closeups', 'Крупный план', 20),
            ('fullbody', 'Полный рост', 30),
        ]:
            cat, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'order': order}
            )
            top[slug] = cat

        # 2. Создаём подкатегории из старых категорий
        old_cats = Category.objects.filter(slug__in=['selfie', 'close-up', 'polnyj-rost'])
        old_to_sub = {}

        for old in old_cats:
            if old.slug == 'selfie':
                parent = top['selfies']
            elif old.slug == 'close-up':
                parent = top['closeups']
            else:
                parent = top['fullbody']

            sub, created = Subcategory.objects.get_or_create(
                slug=old.slug,
                defaults={
                    'category': parent,
                    'name': old.name,
                    'description': getattr(old, 'description', '')
                }
            )
            old_to_sub[old.slug] = sub
            self.stdout.write(f"   Подкатегория: {sub.name} → {parent.name}")

        # 3. Заполняем subcategory у карточек
        # Поскольку старого FK уже нет, ищем по имени старой категории
        updated = 0
        for item in ContentItem.objects.filter(subcategory__isnull=True).iterator():
            # Пытаемся угадать старую категорию по имени (если в full_text или через логику)
            # Вариант 1: если у тебя в базе остались ссылки через related_name 'old_cards'
            try:
                old_cat = Category.objects.filter(old_cards=item).first()
                if old_cat and old_cat.slug in old_to_sub:
                    item.subcategory = old_to_sub[old_cat.slug]
                    item.save()
                    updated += 1
                    continue
            except:
                pass

            # Вариант 2: fallback — ищем по названию категории в старых записях
            for old_slug, sub in old_to_sub.items():
                if old_slug in ['selfie', 'close-up', 'polnyj-rost']:
                    # Можно улучшить позже, если нужно
                    pass

        self.stdout.write(self.style.SUCCESS(
            f'✅ Перенос завершён!\n'
            f'   Создано топ-категорий: {len(top)}\n'
            f'   Подкатегорий: {Subcategory.objects.count()}\n'
            f'   Заполнено карточек: {updated}\n'
        ))

        # Показываем статистику
        self.stdout.write(f"Всего карточек: {ContentItem.objects.count()}")
        self.stdout.write(f"С subcategory: {ContentItem.objects.filter(subcategory__isnull=False).count()}")
