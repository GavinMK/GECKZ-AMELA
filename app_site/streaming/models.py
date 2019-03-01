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
    #password?
    email = models.CharField(max_length=30)
    last_login = models.DateTimeField()
