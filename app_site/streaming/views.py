# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.shortcuts import render

from .decorators import anonymous_only_redirect, subscription_required, relog_required

from .models import *
from django.db.models import Q
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .forms import user_form, login_form, search_form, message_form, mark_message_as_read_form, billing_form, change_form, CommentForm

from django.core.paginator import Paginator
import re


def validate_password(password_candidate):
    valid = False
    if len(password_candidate) > 7:
        if any(char.isdigit() for char in password_candidate):
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
        'error_message': None,
        'next': None
    }
    if request.method == 'POST':
        form = login_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(username=data['username'], password=data['password'])
            if user is not None:
                login(request, user)
                redirect = request.POST.get('redirect')
                print(redirect)
                print("G")
                if redirect != 'None':
                    return HttpResponseRedirect(redirect)
                else:
                    return HttpResponseRedirect(reverse('streaming:homepage'))
            else:
                context['error_message'] = "Wrong username or password"
    elif request.method == 'GET':
        context['next'] = request.GET.get('next')
    return render(request, 'streaming/login.html', context)


@login_required(login_url='streaming:login')
def logout_requested(request):
    logout(request)
    return HttpResponseRedirect(reverse('streaming:login'))


@login_required(login_url='streaming:login')
def movies(request):
    template = loader.get_template('streaming/mediaList.html')
    movie_list = Movie.objects.all()
    context = {
        'media': movie_list,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def shows(request):
    template = loader.get_template('streaming/mediaList.html')
    show_list = TVShow.objects.all()
    context = {
        'media': show_list,
    }
    return HttpResponse(template.render(context, request))

@login_required(login_url='streaming:login')
def post_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        redirect = ''
        if form.is_valid():
            section = None
            clean = form.cleaned_data
            redirect = clean['url']
            url = clean['url'].replace("%20", " ")
            media_match = re.match(r'.*/media/(?P<media_title>[^/]*)/(?P<season>\d+)?/?(?P<episode>\d+)?', url)
            if media_match:
                title = media_match.group('media_title')
                season = media_match.group('season')
                episode = media_match.group('episode')
                media = None
                if TVShow.objects.filter(title=title).exists():
                    media = TVShow.objects.get(title=title)
                    if season:
                        season = TVSeason.objects.get(part_of=media, season_number=int(season))
                        section = TVEpisode.objects.get(part_of=season, episode_number=int(episode)).comment_section
                if not media:
                    media = Movie.objects.get(title=title)
                if not section:
                    section = media.comment_section
            else:
                if len(url) == 20:
                    section = request.user.comment_section
                else:
                    username = url[url[11:].find('/')+12:]
                    if username[-1] == '/': username = username[:-1]
                    section = SiteUser.objects.get(username=username).comment_section

            comment = Comment(posted_by=request.user, content=clean['content'], part_of=section)
            comment.save()

            return HttpResponseRedirect(redirect)
    context['error_message'] = 'Comment too long. Please limit to 500 characters.'
    return render(request, context)



@login_required(login_url='streaming:login')
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


@login_required(login_url='streaming:login')
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


@login_required(login_url='streaming:login')
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

    ratings = Rating.objects.filter(part_of=media.rating_section)
    num_ratings = len(ratings)  # media.rating_section.num_of_ratings

    avg_rating = 0

    for rating in ratings:
        avg_rating += rating.rating
    if num_ratings > 0:
        avg_rating /= num_ratings

    avg_rating_perc = avg_rating * 100 / 5

    actors = Actor.objects.filter(part_of=media.metadata)
    context = {
        'media': media,
        'actors': actors,
        'episodes': episode_list,
        'comments': media.comment_section.comment_set.all().order_by('-timestamp'),
        'avg_rating_perc': avg_rating_perc,
        'avg_rating': avg_rating,
        'num_ratings': num_ratings,


    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
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
        'comments': episode.comment_section.comment_set.all().order_by('-timestamp'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def user_page(request, username=None):
    template = loader.get_template('streaming/userpage.html')
    if not username:
        username = request.user.username
    user = SiteUser.objects.get(username=username)
    media_history = WatchEvent.objects.filter(part_of=user.watch_history)
    if request.method == 'POST':
        if request.POST['follow_button'] == 'Follow':
            request.user.friends.add(user)
        elif request.POST['follow_button'] == 'Unfollow':
            request.user.friends.remove(user)
    context = {
        'user': user,
        'friends': request.user.friends.filter(username=user.username).exists(),
        'comments': user.comment_section.comment_set.all().order_by('-timestamp'),
        'history': media_history.order_by('-time_watched'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def rental_page(request, title):
    template = loader.get_template('streaming/rentPage.html')
    media = Movie.objects.get(title=title)
    if not media:
        return HttpResponse("Invalid media")
    if request.method == 'POST':
        request.user.rentals.add(media)
        return HttpResponseRedirect(reverse('streaming:watch_media', kwargs={'title': title}))
    context = {
        'user': request.user,
        'media': media
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def subscription_page(request, title, season_number, episode_number):
    template = loader.get_template('streaming/subPage.html')
    show = TVShow.objects.get(title=title)
    if not show:
        return HttpResponse("Invalid show")
    season = TVSeason.objects.get(part_of=show, season_number=season_number)
    if not season:
        return HttpResponse("Invalid season number")
    media = TVEpisode.objects.get(part_of=season, episode_number=episode_number)
    if not media:
        return HttpResponse("Invalid episode number")
    if request.method == 'POST':
        request.user.subscriptions.add(show)
        return HttpResponseRedirect(reverse('streaming:watch_media', kwargs={'title': title,
                                                                             'season_number':season_number,
                                                                             'episode_number':episode_number}))
    context = {
        'user': request.user,
        'show':show,
        'season_number': season_number,
        'episode_number': episode_number,
        'media': media
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@subscription_required
def watch_media(request, title, season_number=None, episode_number=None):
    template = loader.get_template('streaming/watchMedia.html')
    media = []
    history = request.user.watch_history
    if Movie.objects.filter(title=title).exists():
        media = Movie.objects.get(title=title)
        watch_event = WatchEvent(movie=media, part_of=history)
        watch_event.save()
    if not media:
        show = TVShow.objects.get(title=title)
        if not show:
            return HttpResponse("Invalid show")
        season = TVSeason.objects.get(part_of=show, season_number=season_number)
        if not season:
            return HttpResponse("Invalid season number")
        media = TVEpisode.objects.get(part_of=season, episode_number=episode_number)
        if not media:
            return HttpResponse("Invalid episode number")
        watch_event = WatchEvent(tv=media, part_of=history)
        watch_event.save()
    if not media:
        return HttpResponse("Invalid Media Request")
    context = {
        'media': media
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def friends(request):
    template = loader.get_template('streaming/friendPage.html')
    friends = request.user.friends.all()
    context = {
        'friends': friends
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def homepage(request):
    template = loader.get_template('streaming/homepage.html')
    show_list = request.user.subscriptions.all()
    movie_list = request.user.rentals.all()
    context = {
        'shows': show_list,
        'movies': movie_list
    }
    return HttpResponse(template.render(context, request))


@relog_required
@login_required(login_url='streaming:login')
def account_page(request):
    return render(request, 'streaming/accountPage.html')


@login_required(login_url='streaming:login')
def inbox(request):
    form = message_form()
    inbox_content = Inbox.objects.all()
    messages = Message.objects.all()
    usernameList = []
    for message in messages:
        usernameList.append(message.part_of.__str__()[:-6])

    messages_and_names = list(zip(messages, usernameList))

    context = {
        'form' : form,
        'error_message' : None,
        'inbox' : inbox_content,
        'messages_list' : messages_and_names,
    }

    if request.method == 'POST':
        if 'send' in request.POST: #user wants to send a message
            form = message_form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user_query = SiteUser.objects.filter(username=data['username'])
                if len(user_query) == 1:

                    user = SiteUser.objects.get(username=data['username'])
                    user_inbox = user.inbox

                    if (user != SiteUser.objects.get(username=request.user.username)):
                        new_message = Message(content=data['content'], from_user=SiteUser.objects.get(username=request.user.username), part_of=user_inbox)
                        new_message.save()
                        user_inbox.num_messages += 1
                        user_inbox.num_unread_messages += 1
                        user_inbox.save()
                        return HttpResponseRedirect(reverse('streaming:inbox'))
                    else:
                        context['error_message'] = "You cannot send a message to yourself"

                else:
                    context['error_message'] = "That user does not exist"

        elif 'read' in request.POST: #user wants to mark the message as read
            form = mark_message_as_read_form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                for message in messages:
                    if (message.__str__() == data['read']):
                        message.read = True
                        message.part_of.num_read_messages += 1
                        message.part_of.num_unread_messages -= 1
                        message.save() #save the changes to the Message object
                        message.part_of.save() #save the changes to the Inbox object
                        return HttpResponseRedirect(reverse('streaming:inbox'))

    return render(request, 'streaming/inbox.html', context)


@login_required(login_url='streaming:login')
def billing(request):
    form = billing_form()
    return render(request, 'streaming/billing.html', {'form': form})


@login_required(login_url='streaming:login')
def change(request):
    form = change_form()
    return render(request, 'streaming/changeInfo.html', {'form': form})
