# Generated by Django 3.2.6 on 2021-12-23 00:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('reaction', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'track'), ('model', 'Track')), models.Q(('app_label', 'set'), ('model', 'Set')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
        migrations.AlterField(
            model_name='repost',
            name='content_type',
            field=models.ForeignKey(limit_choices_to=models.Q(models.Q(('app_label', 'track'), ('model', 'Track')), models.Q(('app_label', 'set'), ('model', 'Set')), _connector='OR'), on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype'),
        ),
    ]
