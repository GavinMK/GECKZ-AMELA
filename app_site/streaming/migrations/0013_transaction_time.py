# Generated by Django 2.1.7 on 2019-04-17 03:53

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0012_siteuser_bio'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='time',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
