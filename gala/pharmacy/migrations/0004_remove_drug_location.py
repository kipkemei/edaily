# Generated by Django 3.0.5 on 2020-05-04 16:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pharmacy', '0003_auto_20200504_1923'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='drug',
            name='location',
        ),
    ]