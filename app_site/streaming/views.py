# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from django.urls import reverse

from datetime import datetime

from django.shortcuts import render

from .decorators import anonymous_only_redirect


from .models import *

from django.db import models

from django.utils import timezone

from django.template import loader

from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout
from .forms import user_form, login_form


def validate_password(password_candidate):
    valid = False
    if len(password_candidate) > 7:
        if any(char.isdigit()for char in password_candidate):
            valid = any(char.isupper() for char in password_candidate)
    return valid


def generate_user(data):
    # May need to figure out how to do it with the foreign keys
    preferences = Preferences()
    preferences.save()
    comment_section = CommentSection()
    comment_section.save()
    inbox = Inbox()
    inbox.save()
    billing = Billing()
    billing.save()
    return SiteUser.objects.create_user(data['username'], email=data['email'], password=data['password'],
                                        first_name=data['first_name'], last_name=data['last_name'],
                                        preferences=preferences, comment_section=comment_section,
                                        inbox=inbox, billing=billing)


@login_required(login_url='login/')
def index(request):
    template = loader.get_template('streaming/index.html')
    context = {
        'objects': SiteUser.objects.values(),
        'movie': Movie.objects.values(),
        'show': TVShow.objects.values(),
        'meta': Metadata.objects.values(),
        'pokemon': Movie.objects.filter(title='Pokemon'),
        'user': request.user.username
    }
    return HttpResponse(template.render(context, request))


@anonymous_only_redirect
def create_user_page(request):
    form = user_form()
    context = {
        'form': form,
        'error_message': None
    }
    if request.method == 'POST':
        form = user_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_query = SiteUser.objects.filter(username=data['username'])
            if len(user_query) != 1:
                generate_user(data).save()
                return HttpResponseRedirect(reverse('streaming:homepage'))
            else:
                context['error_message'] = "That user already exists"
    return render(request, 'streaming/createUser.html', context)


@anonymous_only_redirect
def login_page(request):
    form = login_form()
    context = {
        'form': form,
        'error_message': None
    }
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('streaming:homepage'))
            else:
                context['error_message'] = "Wrong username or password"
    return render(request, 'streaming/login.html', context)


@login_required(login_url='login/')
def logout_requested(request):
    logout(request)
    return HttpResponseRedirect(reverse('streaming:login'))


@login_required(login_url='login/')
def movies(request):
    template = loader.get_template('streaming/mediaList.html')
    movie_list = Movie.objects.all()
    context = {
        'media': movie_list,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def shows(request):
    template = loader.get_template('streaming/mediaList.html')
    show_list = TVShow.objects.all()
    context = {
        'media': show_list,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def display_media(request, title):
    template = loader.get_template('streaming/mediaDisplay.html')
    media = Movie.objects.filter(title=title)
    if not media: media = TVShow.objects.filter(title=title)
    if not media: return HttpResponse("Invalid Media Request")

    actors = Actor.objects.filter(part_of=media[0].metadata)
    context = {
        'media': media,
        'actors': actors,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def display_episode(request, title, season_number, episode_number):
    template = loader.get_template('streaming/tvEpisode.html')
    show = TVShow.objects.filter(title=title)
    if not show: return HttpResponse("Invalid show")
    season = TVSeason.objects.filter(part_of=show[0], season_number=season_number)
    if not season: return HttpResponse("Invalid season number")
    episode = TVEpisode.objects.filter(part_of=season[0], episode_number=episode_number)
    if not episode: return HttpResponse("Invalid episode number")

    actors = Actor.objects.filter(part_of=episode[0].metadata)
    context = {
        'show': show,
        'episode': episode,
        'actors': actors,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def homepage(request):
    return render(request, 'streaming/homepage.html')
