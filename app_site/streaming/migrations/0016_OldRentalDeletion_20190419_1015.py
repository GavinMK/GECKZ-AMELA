# Generated by Django 2.1.7 on 2019-04-19 17:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('streaming', '0015_preferences_inbox_opt_in'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rental',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_rented', models.DateTimeField(default=django.utils.timezone.now)),
                ('duration', models.IntegerField(default=24)),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.Movie')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_rented', models.DateTimeField(default=django.utils.timezone.now)),
                ('show', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='streaming.TVShow')),
            ],
        ),
        migrations.RemoveField(
            model_name='siteuser',
            name='rentals',
        ),
        migrations.RemoveField(
            model_name='siteuser',
            name='subscriptions',
        ),
        migrations.AddField(
            model_name='subscription',
            name='siteuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='rental',
            name='siteuser',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]