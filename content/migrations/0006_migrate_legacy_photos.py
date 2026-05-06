from django.db import migrations

def migrate_legacy_photos(apps, schema_editor):
    ContentItem = apps.get_model('content', 'ContentItem')
    ContentItemPhoto = apps.get_model('content', 'ContentItemPhoto')
    
    migrated = 0
    for item in ContentItem.objects.filter(photo__isnull=False).iterator():
        if not item.photos.exists():
            ContentItemPhoto.objects.create(
                content_item=item,
                photo=item.photo,
                order=0
            )
            migrated += 1
    
    print(f"\n✅ Перенесено старых фото: {migrated}\n")

class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_alter_contentitem_photo_alter_group_subcategories_and_more'),
    ]

operations = [
        migrations.RunPython(migrate_legacy_photos, reverse_code=migrations.RunPython.noop),
    ]
