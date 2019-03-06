# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

# Register your models here.

from streaming.models import *

admin.site.register(Preferences)
admin.site.register(Metadata)
admin.site.register(Billing)
admin.site.register(CommentSection)
admin.site.register(Comment)
admin.site.register(RatingSection)
admin.site.register(Rating)
admin.site.register(Inbox)
admin.site.register(User)
admin.site.register(Message)
admin.site.register(TVShow)
admin.site.register(TVSeason)
admin.site.register(TVEpisode)
admin.site.register(Movie)
admin.site.register(Actor)


