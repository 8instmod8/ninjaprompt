# content/migrations/0003_migrate_display_type_data.py
from django.db import migrations


def migrate_display_type(apps, schema_editor):
    """Переносим display_type из категории в каждую карточку"""
    ContentItem = apps.get_model('content', 'ContentItem')

    count = 0
    for item in ContentItem.objects.select_related(
        'category', 'subcategory__category'
    ).iterator():
        if item.subcategory and item.subcategory.category:
            cat = item.subcategory.category
        elif item.category:
            cat = item.category
        else:
            cat = None

        item.display_type = getattr(cat, 'display_type', 'single')
        item.save(update_fields=['display_type'])
        count += 1

    print(f"✅ Успешно перенесено display_type для {count} карточек")


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0002_add_contentitem_display_type'),
    ]

    operations = [
        migrations.RunPython(migrate_display_type, reverse_code=migrations.RunPython.noop),
    ]
