# Generated by Django 2.1.7 on 2019-04-17 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0013_transaction_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='siteuser',
            name='profile_picture',
            field=models.CharField(default='/profile_pictures/export.png', max_length=100),
        ),
    ]
