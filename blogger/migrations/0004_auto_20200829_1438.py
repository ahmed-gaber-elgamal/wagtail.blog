# Generated by Django 3.0 on 2020-08-29 14:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogger', '0003_auto_20200829_1428'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='blogpage',
            name='tags',
        ),
        migrations.DeleteModel(
            name='BlogPageTag',
        ),
    ]
