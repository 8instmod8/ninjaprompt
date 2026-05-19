from django.core.validators import FileExtensionValidator
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0005_add_video_card_model'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentitemphoto',
            name='photo',
            field=models.ImageField(
                upload_to='photos/multiple/%Y/%m/%d/',
                validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp', 'gif'])],
                verbose_name='Фото',
            ),
        ),
        migrations.AlterField(
            model_name='videocard',
            name='video',
            field=models.FileField(
                upload_to='videos/%Y/%m/%d/',
                validators=[FileExtensionValidator(['mp4', 'webm', 'mov'])],
                verbose_name='Видео файл',
            ),
        ),
        migrations.AlterField(
            model_name='videocard',
            name='video_poster',
            field=models.ImageField(
                upload_to='videos/posters/%Y/%m/%d/',
                blank=True,
                null=True,
                validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
                verbose_name='Постер (превью)',
            ),
        ),
        migrations.AlterField(
            model_name='videocardreference',
            name='photo',
            field=models.ImageField(
                upload_to='videos/references/%Y/%m/%d/',
                validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
                verbose_name='Референсное фото',
            ),
        ),
    ]