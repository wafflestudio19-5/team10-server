# Generated by Django 3.2.6 on 2022-01-06 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('set', '0004_alter_set_permalink'),
    ]

    operations = [
        migrations.AddField(
            model_name='set',
            name='image',
            field=models.URLField(null=True, unique=True),
        ),
    ]
