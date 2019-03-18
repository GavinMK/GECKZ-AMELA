# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField



# Register your models here.

from streaming.models import *
from django import forms

from django.contrib.auth.forms import UserChangeForm


class SiteUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = SiteUser
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        p1 = Preferences()
        p1.save()
        i1 = Inbox()
        i1.save()
        b1 = Billing()
        b1.save()
        c1 = CommentSection()
        c1.save()
        w1 = WatchHistory()
        w1.save()
        user.preferences = p1
        user.inbox = i1
        user.billing = b1
        user.comment_section = c1
        user.watch_history = w1
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    add_form = SiteUserCreationForm

    add_fieldsets = (
            (None, {
                'classes': ('wide',),
                'fields': ('username', 'password1', 'password2', 'first_name', 'last_name', 'email', 'watch_history',)}
             ),
    )


admin.site.register(Preferences)
admin.site.register(Metadata)
admin.site.register(Billing)
admin.site.register(CommentSection)
admin.site.register(Comment)
admin.site.register(RatingSection)
admin.site.register(Rating)
admin.site.register(Inbox)
admin.site.register(SiteUser, UserAdmin)
admin.site.register(Message)
admin.site.register(TVShow)
admin.site.register(TVSeason)
admin.site.register(TVEpisode)
admin.site.register(Movie)
admin.site.register(Actor)
admin.site.register(WatchHistory)
admin.site.register(WatchEvent)
