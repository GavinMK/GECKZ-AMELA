# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta


class Preferences(models.Model):
    email_opt_in = models.BooleanField(default=True)

    def __str__(self):
        query = SiteUser.objects.filter(preferences=self)
        return "Unassigned" if len(query) == 0 else query[0]


class Metadata(models.Model):
    title = models.CharField(max_length=50)
    genre = models.CharField(max_length=50)
    release_year = models.IntegerField(default=0)
    studio = models.CharField(max_length=50)
    streaming_service = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Actor(models.Model):
    name = models.CharField(max_length=50)
    part_of = models.ManyToManyField(Metadata, blank=True)

    def __str__(self):
        return self.name


class Billing(models.Model):
    name = models.CharField(default='', max_length=50)
    cc_num = models.BigIntegerField(default=0)
    cvc_num = models.IntegerField(default=0)
    exp_month = models.IntegerField(default=0)
    exp_year = models.IntegerField(default=0)
    unsub_list = models.ManyToManyField('tvshow', blank=True)
    next_payment_date = models.DateField(default=timezone.now)

    def __str__(self):
        query = SiteUser.objects.filter(billing=self)
        return "Unassigned" if len(query) == 0 else str(query[0])

    def change_date(self):
        self.next_payment_date = datetime.now().date() + timedelta(30)
        self.save()

    def cancel(self):
        self.cc_num = 0
        self.cvc_num = 0
        self.exp_month = 0
        self.exp_year = 0
        self.name = ""
        self.save()


class Transaction(models.Model):
    amount = models.FloatField(default=0)
    charged_to = models.ForeignKey('siteuser', on_delete=models.CASCADE)
    part_of = models.ForeignKey(Billing, on_delete=models.CASCADE)
    statement = models.CharField(default='charge', max_length=50)
    time = models.DateField(default=timezone.now)


class CommentSection(models.Model):
    num_comments = models.IntegerField(default=0)

    def __str__(self):
        tv_query = TVShow.objects.filter(comment_section=self)
        if tv_query: return tv_query[0].__str__() + ' Comment Section'
        ep_query = TVEpisode.objects.filter(comment_section=self)
        if ep_query: return ep_query[0].__str__() + ' Comment Section'
        movie_query = Movie.objects.filter(comment_section=self)
        if movie_query: return movie_query[0].__str__() + ' Comment Section'
        user_query = SiteUser.objects.filter(comment_section=self)
        if user_query: return user_query[0].__str__() + ' Comment Section'
        return 'Unassigned'


class RatingSection(models.Model):
    num_of_ratings = models.IntegerField(default=0)

    def __str__(self):
        tv_query = TVShow.objects.filter(rating_section=self)
        if tv_query: return tv_query[0].__str__() + ' Rating Section'
        ep_query = TVEpisode.objects.filter(rating_section=self)
        if ep_query: return ep_query[0].__str__() + ' Rating Section'
        movie_query = Movie.objects.filter(rating_section=self)
        if movie_query: return movie_query[0].__str__() + ' Rating Section'
        return 'Unassigned'


class Inbox(models.Model):
    num_messages = models.IntegerField(default=0)
    num_read_messages = models.IntegerField(default=0)
    num_unread_messages = models.IntegerField(default=0)

    def __str__(self):
        user = SiteUser.objects.filter(inbox=self)
        if user: return user[0].__str__() + ' Inbox'
        return 'Unassigned'


class Media(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(default='')
    air_date = models.DateField(auto_now=True)
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE)
    comment_section = models.OneToOneField(CommentSection, on_delete=models.CASCADE)
    rating_section = models.OneToOneField(RatingSection, on_delete=models.CASCADE)
    thumbnail_path = models.TextField(default='')

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class PlayableMedia(models.Model):
    file_location = models.CharField(max_length=100)
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

    def __str__(self):
        return self.part_of.title.__str__() + ' Season ' + str(self.season_number) or ''


class TVEpisode(Media, PlayableMedia):
    title = models.CharField(max_length=50)
    episode_number = models.IntegerField(default=0)
    part_of = models.ForeignKey(TVSeason, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Movie(Media, PlayableMedia):
    pass


class WatchEvent(models.Model):
    tv = models.ForeignKey(TVEpisode, on_delete=models.CASCADE, blank=True, null=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, blank=True, null=True)
    time_watched = models.DateTimeField(default=timezone.now)
    part_of = models.ForeignKey('WatchHistory', on_delete=models.CASCADE)

    def __str__(self):
        user = None
        media = self.tv if self.tv else self.movie
        if SiteUser.objects.filter(watch_history = self.part_of).exists() and media:
            user = SiteUser.objects.get(watch_history = self.part_of)
            return user.__str__() + ' watched ' + media.__str__() + ' at ' + self.time_watched.strftime('%x %X')
        return 'Unassigned Event'


class WatchHistory(models.Model):

    def __str__(self):
        if SiteUser.objects.filter(watch_history=self).exists():
            return SiteUser.objects.get(watch_history=self).__str__() + ' Watch History'
        return 'Unassigned Watch History'


class SiteUser(AbstractUser):
    preferences = models.OneToOneField(Preferences, on_delete=models.CASCADE)
    comment_section = models.OneToOneField(CommentSection, on_delete=models.CASCADE)
    inbox = models.OneToOneField(Inbox, on_delete=models.CASCADE)
    billing = models.OneToOneField(Billing, on_delete=models.CASCADE)
    subscriptions = models.ManyToManyField(TVShow, blank=True)
    rentals = models.ManyToManyField(Movie, blank=True)
    watch_history = models.OneToOneField(WatchHistory, null=True, on_delete=models.CASCADE)
    friends = models.OneToOneField('friend', null=True, on_delete=models.CASCADE)
    profile_picture = models.FileField(upload_to='profile_pictures/',  default='/profile_pictures/export.png')

    def __str__(self):
        return self.username


class Friend(models.Model):
    follows = models.ManyToManyField(SiteUser, blank=True)


class Comment(models.Model):
    content = models.CharField(max_length=500)
    timestamp = models.DateTimeField(default=timezone.now)
    part_of = models.ForeignKey(CommentSection, on_delete=models.CASCADE)
    posted_by = models.ForeignKey(SiteUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.part_of.__str__() + ' comment by ' + self.posted_by.__str__() + ' at ' + self.timestamp.strftime('%x %X')


class Rating(models.Model):
    rating = models.IntegerField(default=0)
    part_of = models.ForeignKey(RatingSection, on_delete=models.CASCADE)
    posted_by = models.ForeignKey(SiteUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.part_of.__str__() + ' rating by ' + self.posted_by.__str__() + ' = ' + str(self.rating)


class Message(models.Model):
    content = models.CharField(max_length=3000)
    timestamp = models.DateTimeField(default=timezone.now)
    from_user = models.ForeignKey(SiteUser, on_delete=models.CASCADE)
    part_of = models.ForeignKey(Inbox, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)

    def __str__(self):
        return self.part_of.__str__() + ' message from ' + self.from_user.__str__() + ' at ' + self.timestamp.strftime('%x %X')
