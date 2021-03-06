# Generated by Django 3.2.6 on 2022-01-06 08:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('track', '0004_alter_track_permalink'),
        ('comment', '0005_merge_20220104_0623'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='parent_comment',
        ),
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('track', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_groups', to='track.track')),
            ],
        ),
        migrations.AddField(
            model_name='comment',
            name='group',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='comment.group'),
            preserve_default=False,
        ),
    ]
