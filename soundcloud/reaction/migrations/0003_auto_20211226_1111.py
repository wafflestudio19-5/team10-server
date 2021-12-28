# Generated by Django 3.2.6 on 2021-12-26 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reaction', '0002_auto_20211223_0036'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='like',
            constraint=models.UniqueConstraint(fields=('user', 'content_type', 'object_id'), name='like_unique'),
        ),
        migrations.AddConstraint(
            model_name='repost',
            constraint=models.UniqueConstraint(fields=('user', 'content_type', 'object_id'), name='repost_unique'),
        ),
    ]