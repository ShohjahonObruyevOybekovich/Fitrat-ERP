# Generated by Django 5.1.5 on 2025-06-30 07:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('archived', '0002_initial'),
        ('comments', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='archived',
            name='comment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='archived_comments', to='comments.comment'),
        ),
        migrations.AddField(
            model_name='archived',
            name='is_archived',
            field=models.BooleanField(default=False),
        ),
    ]
