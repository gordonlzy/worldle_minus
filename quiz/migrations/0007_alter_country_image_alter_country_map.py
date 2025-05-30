# Generated by Django 5.2 on 2025-04-22 14:32

import quiz.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_alter_country_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='image',
            field=models.ImageField(upload_to=quiz.models.country_image_path),
        ),
        migrations.AlterField(
            model_name='country',
            name='map',
            field=models.ImageField(blank=True, null=True, upload_to=quiz.models.country_map_path),
        ),
    ]
