# Generated by Django 4.2.10 on 2024-03-14 10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0012_remove_answers_audience'),
    ]

    operations = [
        migrations.AddField(
            model_name='audience',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]