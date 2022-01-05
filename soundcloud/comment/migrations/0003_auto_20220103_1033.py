# Generated by Django 3.2.6 on 2022-01-03 10:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0004_alter_track_permalink'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('comment', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='track',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='track.track'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='writer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to=settings.AUTH_USER_MODEL),
        ),
    ]
