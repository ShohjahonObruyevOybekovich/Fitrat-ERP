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
            name='Asos',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
            ],
            options={
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='Asos1_2',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('asos', models.CharField(blank=True, choices=[('asos1', 'asos1'), ('asos2', 'asos2')], max_length=256, null=True)),
                ('ball', models.FloatField(blank=True, default=0, null=True)),
                ('type', models.CharField(blank=True, choices=[('Bonus', 'Bonus'), ('Compensation', 'Compensation')], max_length=256, null=True)),
                ('amount', models.FloatField(blank=True, default=0, null=True)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Bonus',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(blank=True, choices=[('Markazga kelgan o‘quvchi uchun bonus', 'Markazga kelgan o‘quvchi uchun bonus'), ('Yaratilgan buyurtma uchun bonus', 'Yaratilgan buyurtma uchun bonus'), ('Sinov darsiga kelgani uchun bonus', 'Sinov darsiga kelgani uchun bonus'), ("Hizmat ko’rsatgan har bir Aktiv o'quvchi uchun bonus", "Hizmat ko’rsatgan har bir Aktiv o'quvchi uchun bonus"), ("Aktiv o'quvchiga aylangan yangi o’quvchi uchun bonus", "Aktiv o'quvchiga aylangan yangi o’quvchi uchun bonus"), ("Har bir qarzdor bo’lmagan va Aktiv o'quvchi uchun bonus", "Har bir qarzdor bo’lmagan va Aktiv o'quvchi uchun bonus"), ("Jami yangi va aktiv o'quvchi o'quvchilarning 93% dan 94.9% gacha bo'lgan qismi uchun bonus", "Jami yangi va aktiv o'quvchi o'quvchilarning 93% dan 94.9% gacha bo'lgan qismi uchun bonus"), ("Jami yangi va aktiv o'quvchi o'quvchilarning 95% dan 97.9% gacha bo'lgan qismi uchun bonus", "Jami yangi va aktiv o'quvchi o'quvchilarning 95% dan 97.9% gacha bo'lgan qismi uchun bonus"), ("Jami yangi va aktiv o'quvchi o'quvchilarning 98% dan 99.9% gacha bo'lgan qismi uchun bonus", "Jami yangi va aktiv o'quvchi o'quvchilarning 98% dan 99.9% gacha bo'lgan qismi uchun bonus"), ("Jami yangi va aktiv o'quvchi o'quvchilarning 100% gacha bo'lgan qismi uchun bonus", "Jami yangi va aktiv o'quvchi o'quvchilarning 100% gacha bo'lgan qismi uchun bonus"), ("Aktiv o'quvchi soniga bonus", "Aktiv o'quvchi soniga bonus"), ('Bir oyda 10 marta kelgan har bir oquvchi uchun bonus', 'Bir oyda 10 marta kelgan har bir oquvchi uchun bonus'), ('O’quvchi to’lagan summadan foiz beriladi', 'O’quvchi to’lagan summadan foiz beriladi')], max_length=256, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Compensation',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(blank=True, choices=[('Sinov darsiga yozilb kemaganlar uchun jarima (Jarima)', 'Sinov darsiga yozilb kemaganlar uchun jarima (Jarima)'), (' Sinov darsiga keldi lekin activega o’tmaganligi uchun jarima (Jarima)', ' Sinov darsiga keldi lekin activega o’tmaganligi uchun jarima (Jarima)'), ('Agar o’quvchi ketib qolsa jarima yoziladi (Jarima)', 'Agar o’quvchi ketib qolsa jarima yoziladi (Jarima)'), ("Jami qarzdor o'quvchilar sonining 80.1% dan 85% gacha bo'lgan qismi (Jarima)", "Jami qarzdor o'quvchilar sonining 80.1% dan 85% gacha bo'lgan qismi (Jarima)"), ("Jami qarzdor o'quvchilar sonining 70% dan 80.1% gacha bo'lgan qismi (Jarima)", "Jami qarzdor o'quvchilar sonining 70% dan 80.1% gacha bo'lgan qismi (Jarima)"), ("Jami qarzdor o'quvchilar sonining 70% dan kichik bo'lgan qismi (Jarima)", "Jami qarzdor o'quvchilar sonining 70% dan kichik bo'lgan qismi (Jarima)")], max_length=256, null=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Monitoring',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('ball', models.CharField(blank=True, help_text="This ball can not be higher than asos's max_ball !!!", max_length=128, null=True)),
                ('counter', models.IntegerField()),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='monitoring_creator', to=settings.AUTH_USER_MODEL)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_monitoring', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Monitoring',
                'verbose_name_plural': 'Monitoring 3, 12, 13, 14',
            },
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('comment', models.TextField()),
                ('asos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asos4_comments', to='compensation.asos')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asos4_creator_comments', to=settings.AUTH_USER_MODEL)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asos4_user_comments', to=settings.AUTH_USER_MODEL)),
                ('monitoring', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compensation.monitoring')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Monitoring5',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('ball', models.DecimalField(decimal_places=2, max_digits=10)),
                ('student_count', models.CharField(blank=True, max_length=10, null=True)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='Monitoring5_creator_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Monitoring 5',
                'verbose_name_plural': 'Monitoring 5',
            },
        ),
        migrations.CreateModel(
            name='MonitoringAsos1_2',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('asos', models.CharField(blank=True, choices=[('asos1', 'asos1'), ('asos2', 'asos2')], max_length=256, null=True)),
                ('ball', models.FloatField(blank=True, default=0, null=True)),
                ('type', models.CharField(blank=True, choices=[('Bonus', 'Bonus'), ('Compensation', 'Compensation')], max_length=256, null=True)),
                ('amount', models.FloatField(blank=True, default=0, null=True)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256)),
                ('is_editable', models.BooleanField(default=False)),
                ('is_readable', models.BooleanField(default=False)),
                ('is_parent', models.BooleanField(default=False)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Point',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256)),
                ('amount', models.FloatField(blank=True, default=0, null=True)),
                ('max_ball', models.DecimalField(decimal_places=2, max_digits=10)),
                ('asos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compensation.asos')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
            ],
            options={
                'ordering': ['-created_at'],
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='monitoring',
            name='point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='point_monitoring', to='compensation.point'),
        ),
        migrations.CreateModel(
            name='ResultName',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256)),
                ('point_type', models.CharField(choices=[('Percentage', 'Percentage'), ('Ball', 'Ball'), ('Degree', 'Degree')], max_length=10)),
                ('who', models.CharField(blank=True, choices=[('Teacher', 'Teacher'), ('Student', 'Student')], default='Teacher', max_length=10, null=True)),
                ('type', models.CharField(blank=True, choices=[('One', 'One'), ('Two', 'Two')], max_length=10, null=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
            ],
            options={
                'verbose_name': 'Natijalar',
                'verbose_name_plural': 'Natijalar monitoringi',
            },
        ),
        migrations.CreateModel(
            name='ResultSubjects',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256)),
                ('result_type', models.CharField(blank=True, choices=[('Mine', 'Mine'), ('Student', 'Student')], max_length=256, null=True)),
                ('point', models.CharField(blank=True, max_length=10, null=True)),
                ('max_ball', models.CharField(blank=True, max_length=128, null=True)),
                ('level', models.CharField(blank=True, choices=[('Region', 'Region'), ('Regional', 'Regional')], max_length=256, null=True)),
                ('degree', models.CharField(blank=True, choices=[('1', '1'), ('2', '2'), ('3', '3')], max_length=1, null=True)),
                ('university_type', models.CharField(blank=True, choices=[('Personal', 'Personal'), ('National', 'National')], max_length=256, null=True)),
                ('entry_type', models.CharField(blank=True, choices=[('Grant', 'Grant'), ('Contract', 'Contract')], max_length=10, null=True)),
                ('from_point', models.CharField(blank=True, max_length=10, null=True)),
                ('to_point', models.CharField(blank=True, max_length=10, null=True)),
                ('amount', models.CharField(blank=True, max_length=128, null=True)),
                ('is_archived', models.BooleanField(default=False)),
                ('asos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compensation.asos')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='compensation.resultname')),
            ],
            options={
                'verbose_name': 'Monitoring',
                'verbose_name_plural': 'Natija turi',
            },
        ),
        migrations.CreateModel(
            name='MonitoringAsos4',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('ball', models.CharField(blank=True, max_length=128, null=True)),
                ('type', models.CharField(blank=True, choices=[('Olimpiada', 'Olimpiada'), ('Certificate', 'Certificate'), ('University', 'University')], max_length=15, null=True)),
                ('asos', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='compensation.asos')),
                ('creator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='MonitoringAsos4_creator_comments', to=settings.AUTH_USER_MODEL)),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('result', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='compensation.resultname')),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='compensation.resultsubjects')),
            ],
            options={
                'verbose_name': 'Monitoring 4',
                'verbose_name_plural': 'Monitoring 4',
            },
        ),
        migrations.CreateModel(
            name='StudentCatchingMonitoring',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=256)),
                ('from_student', models.CharField(max_length=256)),
                ('to_student', models.CharField(blank=True, max_length=256, null=True)),
                ('type', models.CharField(choices=[('Bonus', 'Bonus'), ('Compensation', 'Compensation')], max_length=256)),
                ('ball', models.FloatField(blank=True, default=0, null=True)),
                ('asos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compensation.asos')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='StudentCatchingMonitoring_teacher', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Monitoring',
                'verbose_name_plural': "O'quvchini olib qolish monitoringi",
            },
        ),
        migrations.CreateModel(
            name='StudentCountMonitoring',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('max_ball', models.DecimalField(decimal_places=2, max_digits=10)),
                ('amount', models.FloatField(blank=True, default=0, null=True)),
                ('type', models.CharField(blank=True, choices=[('PENALTY', 'PENALTY'), ('BONUS', 'BONUS')], max_length=20, null=True)),
                ('from_point', models.CharField(blank=True, max_length=256, null=True)),
                ('to_point', models.CharField(blank=True, max_length=256, null=True)),
                ('asos', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='compensation.asos')),
                ('filial', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='student_count_monitoring_teacher', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Monitoring',
                'verbose_name_plural': "O'quvchini soni monitoringi",
            },
        ),
    ]
