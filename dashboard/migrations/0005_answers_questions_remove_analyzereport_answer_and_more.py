# Generated by Django 4.2.10 on 2024-03-04 06:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_analyzereport'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='analyzereport',
            name='answer',
        ),
        migrations.RemoveField(
            model_name='analyzereport',
            name='question',
        ),
        migrations.AddField(
            model_name='analyzereport',
            name='answer',
            field=models.ManyToManyField(blank=True, null=True, to='dashboard.answers'),
        ),
        migrations.AddField(
            model_name='analyzereport',
            name='question',
            field=models.ManyToManyField(blank=True, null=True, to='dashboard.questions'),
        ),
    ]
