# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Guy(models.Model):
    name = models.CharField(max_length=20, blank=True, null=False, primary_key=True)
    age = models.SmallIntegerField()

    class Meta:
        db_table = 'guy'


class User(models.Model):
    username = models.CharField(max_length=15, primary_key=True, null=False)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    last_login = models.DateTimeField()

class Preferences(models.Model):
    username = models.CharField(max_length=15, primary_key=True, null=False)
    email_opt_in = models.BooleanField(default=True)


class TV_Show(models.Model):
    tv_show_id = models.IntegerField(primary_key=True)
    num_seasons = models.IntegerField()

class TV_Season(models.Model):
    tv_show_id = models.IntegerField(primary_key=True)
    season_number = models.IntegerField()
    num_episodes = models.IntegerField()
    description = models.TextField()
    year = models.IntegerField()

class TV_Episode(models.Model):
    tv_episode_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    air_date = models.DateField()
    episode_number = models.IntegerField()
    runtime = models.TimeField() #may be better way to store this.. unsure
