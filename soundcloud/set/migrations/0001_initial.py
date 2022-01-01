# Generated by Django 3.2.6 on 2022-01-01 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('playlist', 'playlist'), ('album', 'album'), ('ep', 'ep'), ('single', 'single'), ('compilation', 'compilation'), ('station', 'station')], db_index=True, max_length=15)),
                ('permalink', models.SlugField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True)),
                ('is_private', models.BooleanField(default=False)),
            ],
        ),
    ]
