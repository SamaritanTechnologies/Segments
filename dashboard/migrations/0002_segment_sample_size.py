# Generated by Django 4.2.10 on 2024-03-01 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='segment',
            name='sample_size',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
