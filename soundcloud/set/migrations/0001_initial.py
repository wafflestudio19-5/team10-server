# Generated by Django 3.2.6 on 2021-12-27 14:03

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tag', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Set',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('type', models.CharField(choices=[('playlist', 'playlist'), ('album', 'album'), ('ep', 'ep'), ('single', 'single'), ('compilation', 'compilation'), ('station', 'station')], db_index=True, max_length=15)),
                ('permalink', models.CharField(max_length=255)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField(blank=True)),
                ('is_private', models.BooleanField(default=False)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_sets', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(related_name='sets', to='tag.Tag')),
            ],
        ),
    ]