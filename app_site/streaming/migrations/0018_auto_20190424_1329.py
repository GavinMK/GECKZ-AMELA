# Generated by Django 2.1.7 on 2019-04-24 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0017_UpdateRentals_20190419_1017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='billing',
            name='cc_num',
            field=models.CharField(default='', max_length=19),
        ),
    ]