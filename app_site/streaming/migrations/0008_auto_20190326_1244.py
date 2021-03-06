# Generated by Django 2.1.7 on 2019-03-26 19:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0007_message_read'),
    ]

    operations = [
        migrations.RenameField(
            model_name='billing',
            old_name='cc_info',
            new_name='cc_num',
        ),
        migrations.AddField(
            model_name='billing',
            name='cvc_num',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='billing',
            name='exp_month',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='billing',
            name='exp_year',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='billing',
            name='name',
            field=models.CharField(default='', max_length=50),
        ),
    ]
