# Generated by Django 2.1.7 on 2019-04-18 18:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0014_auto_20190417_0035'),
    ]

    operations = [
        migrations.AddField(
            model_name='preferences',
            name='inbox_opt_in',
            field=models.BooleanField(default=True),
        ),
    ]
