# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.shortcuts import render
from .decorators import anonymous_only_redirect, subscription_required
from .models import *
from django.db.models import Q
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import user_form, login_form, billing_form, change_form
from django.core.paginator import Paginator


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
    history = WatchHistory()
    history.save()
    return SiteUser.objects.create_user(data['username'], email=data['email'], password=data['password'],
                                        first_name=data['first_name'], last_name=data['last_name'],
                                        preferences=preferences, comment_section=comment_section,
                                        inbox=inbox, billing=billing, watch_history=history)


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
def search(request):
    template = loader.get_template('streaming/searchPage.html')
    tv_show_list = TVShow.objects.order_by('title')
    movie_list = Movie.objects.order_by('title')
    context = {
        "filters": {
            "Title": 1,
            "Genre": 0,
            "Release Year": 0,
            "Studio": 0,
            "Streaming Service": 0,
            "Actors": 0,
        },
    }
    for filter in context['filters']:
        if request.GET.get(filter) == "on":
            context['filters'][filter] = 1
        else:
            context['filters'][filter] = 0


    query = request.GET.get('q')
    if query:
        words = query.split(" ")
        tv_results = tv_show_list
        movie_results = movie_list
        # We go through each word in the query, and check to make sure it matches at least some of the data
        # Each result has to match all of the words.
        for word in words:
            db_query = Q()
            if context['filters']['Title']:
                db_query |= Q(title__icontains=word)
            if context['filters']['Genre']:
                db_query |= Q(metadata__genre__icontains=word)
            if context['filters']['Release Year']:
                db_query |= Q(metadata__release_year__icontains=word)
            if context['filters']['Studio']:
                db_query |= Q(metadata__studio__icontains=word)
            if context['filters']['Streaming Service']:
                db_query |= Q(metadata__streaming_service__icontains=word)
            if context['filters']['Actors']:
                db_query |= Q(metadata__actor__name__icontains=word)

            partial_tv_results = tv_show_list.filter(db_query)
            partial_movie_results = movie_list.filter(db_query)
            tv_results &= partial_tv_results
            movie_results &= partial_movie_results
        results = tuple(set(tv_results) | set(movie_results))
        context['query'] = query
    else:
        results = tuple(set(tv_show_list) | set(movie_list))
        context['query'] = ""
    paginator = Paginator(results, 8)
    page = request.GET.get('p', 1)
    media = paginator.get_page(page)
    context['media'] = media
    context['count'] = len(results)
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def user_search(request):
    template = loader.get_template('streaming/userSearchPage.html')
    user_list = SiteUser.objects.all()
    context = dict()
    query = request.GET.get('q')
    if query:
        db_query = Q(username__icontains=query)
        results = user_list.filter(db_query)
        context['users'] = results
        context['query'] = query
    else:
        context['users'] = user_list
        context['query'] = ""
    context['count'] = len(context['users'])
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def display_media(request, title):
    template = loader.get_template('streaming/mediaDisplay.html')
    episode_list = []
    media = []
    if Movie.objects.filter(title=title).exists():
        media = Movie.objects.get(title=title)
    if not media:
        media = TVShow.objects.get(title=title)
        season_list = TVSeason.objects.filter(part_of=media)
        for season in season_list:
            episode_list += list(TVEpisode.objects.filter(part_of=season))
    if not media:
        return HttpResponse("Invalid Media Request")

    actors = Actor.objects.filter(part_of=media.metadata)
    context = {
        'media': media,
        'actors': actors,
        'episodes': episode_list,
        'comments': media.comment_section.comment_set.all()
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def display_episode(request, title, season_number, episode_number):
    template = loader.get_template('streaming/tvEpisode.html')
    show = TVShow.objects.get(title=title)
    if not show:
        return HttpResponse("Invalid show")
    season = TVSeason.objects.get(part_of=show, season_number=season_number)
    if not season:
        return HttpResponse("Invalid season number")
    episode = TVEpisode.objects.get(part_of=season, episode_number=episode_number)
    if not episode:
        return HttpResponse("Invalid episode number")

    actors = Actor.objects.filter(part_of=episode.metadata)
    context = {
        'show': show,
        'season_number': season_number,
        'episode_number': episode_number,
        'episode': episode,
        'actors': actors,
        'comments': episode.comment_section.comment_set.all()
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def user_page(request, username=None):
    template = loader.get_template('streaming/userpage.html')
    if not username:
        username = request.user.username
    user = SiteUser.objects.get(username=username)
    media_history = WatchEvent.objects.filter(part_of=user.watch_history)
    context = {
        'user': user,
        'comments': user.comment_section.comment_set.all(),
        'history': media_history.order_by('-time_watched'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
# @subscription_required [uncomment me when users can subscribe/rent]
def watch_media(request, title, season_number=None, episode_number=None):
    template = loader.get_template('streaming/watchMedia.html')
    media = []
    history = request.user.watch_history
    if Movie.objects.filter(title=title).exists():
        media = Movie.objects.get(title=title)
        watch_event = WatchEvent(movie=media, part_of=history)
        watch_event.save()
    if not media and TVEpisode.objects.filter(title=title).exists():
        media = TVEpisode.objects.get(title=title)
        watch_event = WatchEvent(tv=media, part_of=history)
        watch_event.save()
    if not media:
        return HttpResponse("Invalid Media Request")

    print(media)
    context = {
        'media': media
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def friends(request):
    template = loader.get_template('streaming/friendPage.html')
    context = dict()
    return HttpResponse(template.render(context, request))


@login_required(login_url='login/')
def homepage(request):
    return render(request, 'streaming/homepage.html')


@login_required(login_url='login/')
def account_page(request):
    return render(request, 'streaming/accountPage.html')


@login_required(login_url='login/')
def inbox(request):
    template = loader.get_template('streaming/inbox.html')
    inbox_content = Inbox.objects.all()
    messages = Message.objects.all()
    context = {
        'inbox' : inbox_content,
        'messages_list' : messages,
    }
    return HttpResponse(template.render(context, request))


def billing(request):
    form = billing_form()
    return render(request, 'streaming/billing.html', {'form': form})


def change(request):
    form = change_form()
    return render(request, 'streaming/changeInfo.html', {'form': form})
