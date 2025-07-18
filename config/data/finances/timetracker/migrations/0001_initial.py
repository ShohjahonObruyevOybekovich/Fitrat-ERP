# Generated by Django 5.1.5 on 2025-06-28 08:44

import django.db.models.deletion
import django.utils.timezone
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('filial', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Stuff_Attendance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('check_in', models.DateTimeField(blank=True, null=True)),
                ('check_out', models.DateTimeField(blank=True, null=True)),
                ('first_check_in', models.DateTimeField(blank=True, null=True)),
                ('first_check_out', models.DateTimeField(blank=True, null=True)),
                ('not_marked', models.BooleanField(default=False)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.FloatField(default=0)),
                ('actions', models.JSONField(blank=True, null=True)),
                ('action', models.CharField(blank=True, choices=[('In_side', 'In_side'), ('Outside', 'Outside')], max_length=10, null=True)),
                ('status', models.CharField(blank=True, choices=[('Late', 'Late'), ('On_time', 'On_time'), ('Absent', 'Absent')], max_length=10, null=True)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_part_attendance', to=settings.AUTH_USER_MODEL, to_field='second_user')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Employee_attendance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(blank=True, choices=[('In_office', 'In_office'), ('Gone', 'Gone'), ('Absent', 'Absent')], max_length=10, null=True)),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('amount', models.FloatField(default=0)),
                ('employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_attendance', to=settings.AUTH_USER_MODEL, to_field='second_user')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('attendance', models.ManyToManyField(related_name='employee_full_attendance', to='timetracker.stuff_attendance')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='UserTimeLine',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('day', models.CharField(blank=True, choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday'), ('Sunday', 'Sunday')], max_length=120, null=True)),
                ('is_weekend', models.BooleanField(default=False)),
                ('penalty', models.FloatField(default=0)),
                ('bonus', models.FloatField(default=0)),
                ('start_time', models.TimeField(default=django.utils.timezone.now)),
                ('end_time', models.TimeField(default=django.utils.timezone.now)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_timeline', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
    ]
