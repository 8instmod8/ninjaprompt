# content/migrations/00XX_add_contentitem_display_type.py
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0001_initial'),   # ← поменяй на твой последний номер, если другой
    ]

    operations = [
        migrations.AddField(
            model_name='contentitem',
            name='display_type',
            field=models.CharField(
                max_length=20,
                choices=[
                    ('single', 'Одиночное фото'),
                    ('carousel', 'Карусель'),
                    ('slider', 'Шторка (До/После)'),
                ],
                default='single',
                null=True,
                blank=True,
                verbose_name='Тип отображения фото',
                help_text='Выбирается индивидуально для каждой карточки (независимо от категории)',
            ),
        ),
    ]
