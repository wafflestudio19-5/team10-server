# Generated by Django 3.2.6 on 2022-01-13 07:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('set', '0008_auto_20220113_0715'),
    ]

    operations = [
        migrations.RenameField(
            model_name='set',
            old_name='image_info',
            new_name='image_profile',
        ),
    ]
