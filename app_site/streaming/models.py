# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone


class Preferences(models.Model):
    email_opt_in = models.BooleanField(default=True)


class Metadata(models.Model):
    title = models.CharField(max_length=20)
    genre = models.CharField(max_length=20)
    release_year = models.IntegerField(default=0)
    studio = models.CharField(max_length=20)
    streaming_service = models.CharField(max_length=20)

    def __str__(self):
        return self.title


class Actor(models.Model):
    name = models.CharField(max_length=40)
    part_of = models.ForeignKey(Metadata, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Billing(models.Model):
    cc_info = models.BigIntegerField(default=0)
    next_payment_date = models.DateField(default=timezone.now)
    num_sub_slots = models.IntegerField(default=10)
    num_rentals = models.IntegerField(default=0)
    transaction_info = models.CharField(max_length=50)


class CommentSection(models.Model):
    num_comments = models.IntegerField(default=0)


class Comment(models.Model):
    content = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    part_of = models.ForeignKey(CommentSection, on_delete=models.CASCADE)


class RatingSection(models.Model):
    num_of_ratings = models.IntegerField(default=0)


class Rating(models.Model):
    rating = models.IntegerField(default=0)
    part_of = models.ForeignKey(RatingSection, on_delete=models.CASCADE)


class Inbox(models.Model):
    num_messages = models.IntegerField(default=0)
    num_read_messages = models.IntegerField(default=0)
    num_unread_messages = models.IntegerField(default=0)


class Media(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(default='')
    air_date = models.DateField(auto_now=True)
    metadata = models.OneToOneField(Metadata, on_delete=models.CASCADE)
    comment_section = models.OneToOneField(CommentSection, on_delete=models.CASCADE)
    rating_section = models.OneToOneField(RatingSection, on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class PlayableMedia(models.Model):
    file_location = models.CharField(max_length=50)
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
    title = models.CharField(max_length=25)
    episode_number = models.IntegerField(default=0)
    part_of = models.ForeignKey(TVSeason, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Movie(Media, PlayableMedia):
    pass


class User(models.Model):
    username = models.CharField(max_length=15)
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    email = models.CharField(max_length=30)
    last_login = models.DateTimeField(default=timezone.now)
    preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE)
    comment_section = models.OneToOneField(CommentSection, on_delete=models.CASCADE)
    inbox = models.OneToOneField(Inbox, on_delete=models.CASCADE)
    billing = models.OneToOneField(Billing, on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField(TVShow, blank=True)
    rentals = models.ManyToManyField(Movie, blank=True)

    def __str__(self):
        return self.username


class Message(models.Model):
    content = models.CharField(max_length=20)
    timestamp = models.DateTimeField(default=timezone.now)
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    part_of = models.ForeignKey(Inbox, on_delete=models.CASCADE)