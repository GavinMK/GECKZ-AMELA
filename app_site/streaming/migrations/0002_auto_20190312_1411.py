# Generated by Django 2.1.7 on 2019-03-12 21:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='title',
            field=models.CharField(max_length=40),
        ),
    ]
