# Generated by Django 3.2.6 on 2021-11-25 05:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_auto_20211124_1737'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='age',
        ),
        migrations.AddField(
            model_name='user',
            name='birthday',
            field=models.DateField(default=datetime.date(2021, 11, 25)),
        ),
    ]