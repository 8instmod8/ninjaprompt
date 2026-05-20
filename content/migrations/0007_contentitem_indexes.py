from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0006_add_file_validators'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='contentitem',
            index=models.Index(fields=['-created_at'], name='content_con_created_88163b_idx'),
        ),
        migrations.AddIndex(
            model_name='contentitem',
            index=models.Index(fields=['category', 'subcategory'], name='content_con_categor_902d0f_idx'),
        ),
    ]