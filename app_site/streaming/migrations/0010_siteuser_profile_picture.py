# Generated by Django 2.1.7 on 2019-04-11 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0009_auto_20190408_2124'),
    ]

    operations = [
        migrations.AddField(
            model_name='siteuser',
            name='profile_picture',
            field=models.FileField(default='/profile_pictures/export.png', upload_to='profile_pictures/'),
        ),
    ]
