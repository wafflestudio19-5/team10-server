# Generated by Django 3.2.6 on 2021-12-18 08:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0010_merge_0007_follow_0009_user_permalink'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='user',
            name='is_staff',
            field=models.BooleanField(default=False),
        ),
    ]
