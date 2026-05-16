from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0002_reset_history'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentitem',
            name='video',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to='videos/%Y/%m/%d/',
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['mp4', 'webm'])],
                verbose_name='Видео файл'
            ),
        ),
        migrations.AddField(
            model_name='contentitem',
            name='video_poster',
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to='videos/posters/%Y/%m/%d/',
                verbose_name='Постер для видео'
            ),
        ),
    ]
