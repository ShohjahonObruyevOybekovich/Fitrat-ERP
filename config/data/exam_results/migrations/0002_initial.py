# Generated by Django 5.1.5 on 2025-06-28 08:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('exam_results', '0001_initial'),
        ('filial', '0001_initial'),
        ('groups', '0002_initial'),
        ('quiz', '0001_initial'),
        ('student', '0001_initial'),
        ('subject', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizresult',
            name='Listening',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.listening'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='cloze_test',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.cloze_test'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='filial',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='image_objective',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.imageobjectivetest'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='match_pair',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.matchpairs'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='objective',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.objectivetest'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='questions',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.question'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quiz_results', to='quiz.quiz'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='student.student'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='true_false',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.true_false'),
        ),
        migrations.AddField(
            model_name='quizresult',
            name='vocabulary',
            field=models.ManyToManyField(related_name='quiz_results', to='quiz.vocabulary'),
        ),
        migrations.AddField(
            model_name='unittest',
            name='filial',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial'),
        ),
        migrations.AddField(
            model_name='unittest',
            name='group',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unit_test_group', to='groups.group'),
        ),
        migrations.AddField(
            model_name='unittest',
            name='quiz',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.quiz'),
        ),
        migrations.AddField(
            model_name='unittest',
            name='theme_after',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='unit_test_theme_after', to='subject.theme'),
        ),
        migrations.AddField(
            model_name='unittest',
            name='themes',
            field=models.ManyToManyField(related_name='unit_test_themes', to='subject.theme'),
        ),
        migrations.AddField(
            model_name='unittestresult',
            name='filial',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='filial.filial'),
        ),
        migrations.AddField(
            model_name='unittestresult',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='student.student'),
        ),
        migrations.AddField(
            model_name='unittestresult',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='exam_results.unittest'),
        ),
    ]
