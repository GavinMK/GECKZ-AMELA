# Generated by Django 2.1.7 on 2019-03-20 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0006_siteuser_friends'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='read',
            field=models.BooleanField(default=False),
        ),
    ]
