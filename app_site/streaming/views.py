# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from django.shortcuts import render

from .decorators import anonymous_only_redirect, subscription_required, relog_required
from .util import *
from .constants import *
from .models import *
from django.db.models import Q
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import user_form, login_form, search_form, message_form, mark_message_as_read_form, billing_form, change_info, CommentForm, profile_form

from django.core.paginator import Paginator
import re

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
        'media': movie_list.order_by('title'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def shows(request):
    template = loader.get_template('streaming/mediaList.html')
    show_list = TVShow.objects.all()
    context = {
        'media': show_list.order_by('title'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def post_comment(request):
    context = {
        'error_message': None
    }
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            redirect = clean['url']
            section = get_comment_section(redirect)
            comment = Comment(posted_by=request.user, content=clean['content'], part_of=section)
            comment.save()

            return HttpResponseRedirect(redirect)
    context['error_message'] = 'Comment too long. Please limit to 500 characters.'
    return HttpResponseRedirect(reverse('streaming:homepage'))


@login_required(login_url='streaming:login')
def search(request):
    template = loader.get_template('streaming/searchPage.html')
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
    tv_show_list = TVShow.objects.order_by('title')
    movie_list = Movie.objects.order_by('title')
    for filter in context['filters']:
        if request.GET.get(filter) == "on":
            context['filters'][filter] = 1
        else:
            context['filters'][filter] = 0

    query = request.GET.get('q')
    if query:
        results = filter_db_query(context, query, tv_show_list, movie_list)
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
    media = get_media(title)
    if type(media) is TVShow:
        season_list = TVSeason.objects.filter(part_of=media).order_by('season_number')
        for season in season_list:
            episode_list += list(TVEpisode.objects.filter(part_of=season).order_by('episode_number'))

    ratings = Rating.objects.filter(part_of=media.rating_section)
    num_ratings = len(ratings)
    calc = get_rating(ratings)
    avg_rating_perc = calc[0]
    avg_rating = calc[1]

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
    show = get_media(title)
    episode = get_episode(show, season_number, episode_number)

    actors = Actor.objects.filter(part_of=episode.metadata)

    ratings = Rating.objects.filter(part_of=episode.rating_section)
    num_ratings = len(ratings)
    calc = get_rating(ratings)
    avg_rating_perc = calc[0]
    avg_rating = calc[1]

    context = {
        'show': show,
        'season_number': season_number,
        'episode_number': episode_number,
        'episode': episode,
        'actors': actors,
        'comments': episode.comment_section.comment_set.all().order_by('-timestamp'),
        'avg_rating_perc': avg_rating_perc,
        'avg_rating': avg_rating,
        'num_ratings': num_ratings,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def user_page(request, username=None):
    template = loader.get_template('streaming/userpage.html')
    if not username:
        username = request.user.username
    user = SiteUser.objects.get(username=username)
    media_history = WatchEvent.objects.filter(part_of=user.watch_history)
    if request.method == 'POST': #user wants to follow/unfollow
        if 'follow_button' in request.POST:
            if request.POST['follow_button'] == 'Follow':
                request.user.friends.follows.add(user)
            elif request.POST['follow_button'] == 'Unfollow':
                request.user.friends.follows.remove(user)
        elif 'message' in request.POST: #user wants to message
            return inbox(request, user)
    context = {
        'user': user,
        'friends': request.user.friends.follows.filter(username=user.username).exists(),
        'friendsList': user.friends.follows.all(),
        'rating':  Rating.objects.filter(posted_by=user).last(),
        'comments': user.comment_section.comment_set.all().order_by('-timestamp'),
        'history': media_history.order_by('-time_watched'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
def rental_page(request, title):
    template = loader.get_template('streaming/rentPage.html')
    media = get_media(title)
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
    show = get_media(title)
    if show is None:
        return HttpResponse("BAD MEDIA")
    exceed_subs = len(request.user.subscriptions.all()) >= MAX_SUBS
    print(len(request.user.subscriptions.all()))
    if request.method == 'POST':
        request.user.subscriptions.add(show)
        return HttpResponseRedirect(reverse('streaming:watch_media', kwargs={'title': title,
                                                                             'season_number':season_number,
                                                                             'episode_number':episode_number}))

    context = {
        'user': request.user,
        'show': show,
        'season_number': season_number,
        'episode_number': episode_number,
        'exceed': exceed_subs
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
def post_rating(request):
    if request.method == 'POST':
        redirect = request.POST['url']
        url = redirect.replace("%20", " ")
        media_match = re.match(r'.*/media/(?P<media_title>[^/]*)/(?P<season>\d+)?/?(?P<episode>\d+)?', url)
        title = media_match.group('media_title')
        season_number = media_match.group('season')
        episode_number = media_match.group('episode')
        media = get_media(title)
        if type(media) is TVShow and episode_number is not None:
            episode = get_episode(media, int(season_number), int(episode_number))
            section = episode.rating_section
        else:
            section = media.rating_section

        rate_number = int(request.POST.get('rating'))
        if rate_number > 5 or rate_number < 1:
            return HttpResponse("Invalid Rating '{0}'".format(rate_number))
        if Rating.objects.filter(part_of=section, posted_by=request.user):
            rating = Rating.objects.get(part_of=section, posted_by=request.user)
        else:
            rating = Rating()
            rating.part_of = section
            rating.posted_by = request.user
            section.num_of_ratings = len(Rating.objects.filter(part_of=section))
            section.save()
        rating.rating = rate_number
        rating.save()

        return HttpResponseRedirect(redirect)
    return HttpResponseRedirect(reverse('streaming:homepage'))


@login_required(login_url='streaming:login')
def friends(request):
    template = loader.get_template('streaming/friendPage.html')
    friends = request.user.friends.follows.all()
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


@login_required(login_url='streaming:login')
def account_page(request):
    return render(request, 'streaming/accountPage.html')


@login_required(login_url='streaming:login')
def inbox(request, sendTo=None):
    form = message_form()
    from_user = request.user
    messages_from = from_user.inbox.message_set.all() #get all of the current user's messages

    if request.method == 'POST':
        if 'read' in request.POST: #user wants to mark the message as read
            form = mark_message_as_read_form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                for message in messages_from:
                    if (message.__str__() == data['read']):
                        message.read = True
                        message.part_of.num_read_messages += 1
                        message.part_of.num_unread_messages -= 1
                        message.save() #save the changes to the Message object
                        message.part_of.save() #save the changes to the Inbox object
                        return HttpResponseRedirect(reverse('streaming:inbox'))

    context = {
        'form': form,
        'messages_from': messages_from,
    }

    return render(request, 'streaming/inbox.html', context)


@login_required(login_url='streaming:login')
def messageInbox(request, sendTo=None):
    form = message_form()
    from_user = request.user

    if sendTo is None:
        sendTo = ''

    context = {
        'form' : form,
        'error_message' : None,
        'sendTo': sendTo,
    }

    if request.method == 'POST':
        if 'send' in request.POST: #user wants to send a message
            form = message_form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                if len(SiteUser.objects.filter(username=data['username'])) == 1: #valid username
                    to_user = SiteUser.objects.get(username=data['username'])
                    if (to_user.username != from_user.username):
                        new_message = Message(content=data['content'], from_user=SiteUser.objects.get(username=request.user.username), part_of=to_user.inbox)
                        new_message.save()
                        to_user.inbox.num_messages += 1
                        to_user.inbox.num_unread_messages += 1
                        to_user.inbox.save()
                        return HttpResponseRedirect(reverse('streaming:inbox'))
                    else:
                        context['error_message'] = "You cannot send a message to yourself"
                else: #invalid username
                    context['error_message'] = "That user does not exist"

    return render(request, 'streaming/messageInbox.html', context)


@login_required(login_url='streaming:login')
def sentInbox(request, sendTo=None):
    from_user = request.user
    messages_to = Message.objects.filter(from_user=from_user)  #get all messages the current user has sent to other inbox's

    context = {
        'messages_to' : messages_to
    }

    return render(request, 'streaming/sentInbox.html', context)


@login_required(login_url='streaming:login')
def readInbox(request, sendTo=None):
    from_user = request.user
    messages_from = from_user.inbox.message_set.all() #get all of the current user's messages

    context = {
        'messages_from' : messages_from
    }

    return render(request, 'streaming/readInbox.html', context)


@login_required(login_url='streaming:login')
def billing(request):
    form = billing_form()
    context = {
        'form' : form,
        'error_message' : None,
    }
    if request.method == 'POST':
        form = billing_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            billings = Billing.objects.all()
            for billing in billings:
                if (str(billing) == str(SiteUser.objects.get(username=request.user.username))):
                    billing.name = data['name']
                    billing.cc_num = data['cc_num']
                    billing.cvc_num = data['cvc_num']
                    billing.exp_month = data['exp_month']
                    billing.exp_year = data['exp_year']
                    billing.save()

            return render(request, 'streaming/accountPage.html')

    return render(request, 'streaming/billing.html', context)

@login_required(login_url='streaming:login')
def editProfile(request):
    form = profile_form()
    return render(request, 'streaming/editProfile.html', {'form': form})

@login_required(login_url='streaming:login')
def change(request):
    form = change_info(request.POST)

    context = {
        'form' : form,
        'error_message' : None,
    }

    if request.method == 'POST':
        if form.is_valid():
            data = form.cleaned_data
            passWord = authenticate(username=request.user.username, password=data['old_password'])

            if passWord is None: #the user entered the wrong password
                context['error_message'] = "Incorrect password. Please retype your current password to change your user information"
                render(request, 'streaming/changeInfo.html', context)
            else:
                user = request.user
                user.username = data['username']
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.email = data['email']

                user.save()

                return render(request, 'streaming/accountPage.html')

    return render(request, 'streaming/changeInfo.html', context)
