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
    username = models.CharField(max_length=15)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    last_login = models.DateTimeField()


class Preferences(models.Model):
    # username = models.CharField(max_length=15, primary_key=True, null=False)
    email_opt_in = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Media(models.Model):
    file_location = models.CharField()
    title = models.CharField(max_length=50)
    description = models.TextField()
    air_date = models.DateField()
    runtime = models.TimeField()  # may be better way to store this.. unsure

    class Meta:
        abstract = True


class TVShow(models.Model):
    # tv_show_id = models.IntegerField(primary_key=True)
    num_seasons = models.IntegerField()


class TVSeason(models.Model):
    # tv_show_id = models.IntegerField(primary_key=True)
    season_number = models.IntegerField()
    num_episodes = models.IntegerField()
    description = models.TextField()
    year = models.IntegerField()
    part_of = models.ForeignKey(TVShow, on_delete=models.CASCADE)


class TVEpisode(Media):
    # tv_episode_id = models.IntegerField(primary_key=True)
    episode_number = models.IntegerField()
    part_of = models.ForeignKey(TVSeason, on_delete=models.CASCADE)


class Billing(models.Model):
    # username = models.CharField(max_length=15, primary_key=True, null=False)
    cc_info = models.IntegerField()
    next_payment_date = models.DateField()
    num_sub_slots = models.IntegerField(default=10)
    num_rentals = models.IntegerField(default=0)
    transaction_info = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Inbox(models.Model):
    #username = models.CharField(max_length=15, primary_key=True, null=False)
    num_messages = models.IntegerField()
    num_read_messages = models.IntegerField()
    num_unread_messages = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Message(models.Model):
    # message_id = models.IntegerField(primary_key=True, null=False)
    content = models.CharField()
    timestamp = models.DateTimeField()
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)


class Movie(Media):
    cost = models.IntegerField()


class Metadata(models.Model):
    title = models.CharField()
    cast = models.CharField()
    genre = models.CharField()
    release_year = models.IntegerField()
    studio = models.CharField()
    streaming_service = models.CharField()
    linked_to = models.ForeignKey(Media, on_delete=models.CASCADE)


class CommentSection(models.Model):
    num_comments = models.IntegerField()

    class Meta:
        abstract = True


class MediaCommentSection(CommentSection):
    owned_by = models.ForeignKey(Media, on_delete=models.CASCADE)


class UserCommentSection(CommentSection):
    owned_by = models.ForeignKey(User, on_delete=models.CASCADE)


class Comment(models.Model):
    content = models.CharField()
    timestamp = models.DateTimeField()
    part_of = models.ForeignKey(CommentSection, on_delete=models.CASCADE)


class RatingSection(models.Model):
    num_of_ratings = models.IntegerField()
    part_of = models.ForeignKey(Media, on_delete=models.CASCADE)


class Rating(models.Model):
    rating = models.IntegerField(max_length=5)
    part_of = models.ForeignKey(RatingSection, on_delete=models.CASCADE)

