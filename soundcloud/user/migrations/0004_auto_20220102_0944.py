# Generated by Django 3.2.6 on 2022-01-02 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0003_merge_0002_alter_user_permalink_0002_user_is_staff'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='image_header',
            field=models.URLField(null=True, unique=True),
        ),
        migrations.AddField(
            model_name='user',
            name='image_profile',
            field=models.URLField(null=True, unique=True),
        ),
    ]
