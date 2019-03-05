# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone


class User(models.Model):
    username = models.CharField(max_length=15)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    last_login = models.DateTimeField(default=timezone.now)


class Preferences(models.Model):
    email_opt_in = models.BooleanField(default=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Metadata(models.Model):
    title = models.CharField(max_length=20)
    cast = models.CharField(max_length=20)
    genre = models.CharField(max_length=20)
    release_year = models.IntegerField(default=0)
    studio = models.CharField(max_length=20)
    streaming_service = models.CharField(max_length=20)


class Media(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(default='')
    air_date = models.DateField(auto_now=True)
    linked_to = models.OneToOneField(Metadata, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class PlayableMedia(models.Model):
    file_location = models.CharField(max_length=20)
    runtime = models.DurationField(default=0)

    class Meta:
        abstract = True


class TVShow(Media):
    num_seasons = models.IntegerField(default=0)


class TVSeason(models.Model):
    season_number = models.IntegerField(default=0)
    num_episodes = models.IntegerField(default=0)
    description = models.TextField(default='')
    year = models.IntegerField(default=0)
    part_of = models.ForeignKey(TVShow, on_delete=models.CASCADE)


class TVEpisode(PlayableMedia):
    episode_number = models.IntegerField(default=0)
    part_of = models.ForeignKey(TVSeason, on_delete=models.CASCADE)


class Movie(Media, PlayableMedia):
    pass


class Billing(models.Model):
    cc_info = models.IntegerField(default=0)
    next_payment_date = models.DateField(default=timezone.now)
    num_sub_slots = models.IntegerField(default=10)
    num_rentals = models.IntegerField(default=0)
    transaction_info = models.CharField(max_length=50)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Inbox(models.Model):
    num_messages = models.IntegerField(default=0)
    num_read_messages = models.IntegerField(default=0)
    num_unread_messages = models.IntegerField(default=0)
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Message(models.Model):
    content = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)


class CommentSection(models.Model):
    num_comments = models.IntegerField(default=0)


class MediaCommentSection(CommentSection):
    owned_by = models.OneToOneField(Media, on_delete=models.CASCADE)


class UserCommentSection(CommentSection):
    owned_by = models.OneToOneField(User, on_delete=models.CASCADE)


class Comment(models.Model):
    content = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    part_of = models.ForeignKey(CommentSection, on_delete=models.CASCADE)


class RatingSection(models.Model):
    num_of_ratings = models.IntegerField(default=0)
    part_of = models.OneToOneField(Media, on_delete=models.CASCADE)


class Rating(models.Model):
    rating = models.IntegerField(default=0)
    part_of = models.ForeignKey(RatingSection, on_delete=models.CASCADE)

