from django.db import migrations


def create_top_level_categories(apps, schema_editor):
    """Создаём новые верхнеуровневые категории"""
    Category = apps.get_model('content', 'Category')

    top_cats = [
        {'name': 'Селфи',        'slug': 'selfies',   'order': 10},
        {'name': 'Крупный план', 'slug': 'closeups',  'order': 20},
        {'name': 'Полный рост',  'slug': 'fullbody',  'order': 30},
    ]

    for data in top_cats:
        Category.objects.get_or_create(slug=data['slug'], defaults=data)


def migrate_existing_data(apps, schema_editor):
    """Переносим старые категории → подкатегории и заполняем связи"""
    OldCategory = apps.get_model('content', 'Category')
    NewCategory = apps.get_model('content', 'Category')
    Subcategory = apps.get_model('content', 'Subcategory')
    ContentItem = apps.get_model('content', 'ContentItem')
    Group = apps.get_model('content', 'Group')

    old_to_sub = {}

    # Создаём подкатегории
    for old in OldCategory.objects.all():
        name_lower = old.name.lower()
        if 'селфи' in name_lower or old.slug == 'selfie':
            parent_slug = 'selfies'
        elif 'крупн' in name_lower or 'close' in old.slug:
            parent_slug = 'closeups'
        elif 'полн' in name_lower or 'rost' in old.slug:
            parent_slug = 'fullbody'
        else:
            parent_slug = 'selfies'

        parent = NewCategory.objects.get(slug=parent_slug)

        sub = Subcategory.objects.create(
            category=parent,
            name=old.name,
            slug=old.slug,
            description=getattr(old, 'description', '')
        )
        old_to_sub[old.slug] = sub

    # Заполняем subcategory у карточек
    for item in ContentItem.objects.all().iterator():
        if getattr(item, 'category_id', None) and item.category.slug in old_to_sub:
            item.subcategory = old_to_sub[item.category.slug]
            item.save()

    # Заполняем группы — используем старое ManyToMany, если оно ещё доступно
    for group in Group.objects.all():
        # Пытаемся получить старые категории через raw relation (если поле ещё существует)
        try:
            old_cats = group.categories.all()   # может упасть
        except AttributeError:
            old_cats = []   # если поле уже удалено

        subs = [old_to_sub[cat.slug] for cat in old_cats if cat.slug in old_to_sub]
        if subs:
            group.subcategories.set(subs)

class Migration(migrations.Migration):
    dependencies = [
        ('content', '0002_alter_category_options_remove_contentitem_category_and_more'),
    ]

    operations = [
        migrations.RunPython(create_top_level_categories, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(migrate_existing_data, reverse_code=migrations.RunPython.noop),
    ]
