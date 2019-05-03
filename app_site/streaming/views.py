# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.urls import reverse
from os import listdir
from django.shortcuts import render, redirect

from .decorators import *
from .util import *
from .constants import *
from .models import *
from django.db.models import Q
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from .forms import user_form, login_form, search_form, message_form, mark_message_as_read_form, billing_form, change_info, CommentForm, profile_form, notifications_form

from django.core.paginator import Paginator
import re
from datetime import datetime, timedelta
from django.core.files.storage import FileSystemStorage

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
def redirect_homepage(request):
    return HttpResponseRedirect(reverse('streaming:homepage'))


@login_required(login_url='streaming:login')
@active_user
def movies(request):
    template = loader.get_template('streaming/mediaList.html')
    movie_list = Movie.objects.all()
    context = {
        'media': movie_list.order_by('title'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
def shows(request):
    template = loader.get_template('streaming/mediaList.html')
    show_list = TVShow.objects.all()
    context = {
        'media': show_list.order_by('title'),
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
def post_comment(request):
    context = {
        'error_message': None
    }
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            clean = form.cleaned_data
            redirect = clean['url']
            section = get_comment_section(request, redirect)
            comment = Comment(posted_by=request.user, content=clean['content'], part_of=section)
            comment.save()

            return HttpResponseRedirect(redirect)
    context['error_message'] = 'Comment too long. Please limit to 500 characters.'
    return HttpResponseRedirect(reverse('streaming:homepage'))

class SearchFilter:

    def __init__(self, name, request, defaults):
        self.name = name
        self.value = request.GET.get(name)
        if self.value is None:
            self.value = ""
        self.defaults = list(sorted(defaults))

    def __str__(self):
        return "{0}: {1} {2}".format(self.name, self.value, self.defaults)


@login_required(login_url='streaming:login')
@active_user
def search(request):
    template = loader.get_template('streaming/searchPage.html')
    all_media = list(Movie.objects.all()) + list(TVShow.objects.all())

    # This method of gathering this data is slow and cumbersome (it scales with the number of movies + number of shows)
    # A better long-term solution would involve storing this stuff in the database
    genres = set()
    for m in all_media:
        g_text = m.metadata.genre
        if g_text:
            gs = g_text.split(", ")
            for g in gs:
                genres.add(g)
    genres = sorted(genres)
    studios = set()
    for m in all_media:
        s_text = m.metadata.studio
        if s_text:
            ss = s_text.split(", ")
            for s in ss:
                studios.add(s)
    studios = sorted(studios)
    stream = set()
    for m in all_media:
        s_text = m.metadata.streaming_service
        if s_text:
            ss = s_text.split(", ")
            for s in ss:
                stream.add(s)
    stream = sorted(stream)

    context = {
        "filters": (
            #["name", "Request value", ("Values","in","the","dropdowns")]
            SearchFilter("Title", request, ()),
            SearchFilter("Genre", request, genres),
            SearchFilter("Release Year", request, ()),
            SearchFilter("Studio", request, studios),
            SearchFilter("Streaming Service", request, stream),
            SearchFilter("Actors", request, (str(a) for a in Actor.objects.all()))
        ),
    }
    tv_show_list = TVShow.objects.order_by('title')
    movie_list = Movie.objects.order_by('title')

    query = request.GET.get('Title')
    results = filter_db_query(context, tv_show_list, movie_list)
    context['query'] = query

    paginator = Paginator(results, 8)
    page = request.GET.get('p', 1)
    media = paginator.get_page(page)
    context['media'] = media
    context['count'] = len(results)
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
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
@active_user
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

    unsub_queued = title in [str(show) for show in request.user.billing.unsub_list.all()]

    actors = Actor.objects.filter(part_of=media.metadata)
    context = {
        'subscribed': request.user.subscriptions.all().filter(title=media.title),
        'unsub_queued': unsub_queued,
        'media': media,
        'actors': actors,
        'episodes': episode_list,
        'comments': paginate_comments(request, media.comment_section),
        'avg_rating_perc': avg_rating_perc,
        'avg_rating': avg_rating,
        'num_ratings': num_ratings,


    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
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
        'comments': paginate_comments(request, episode.comment_section),
        'avg_rating_perc': avg_rating_perc,
        'avg_rating': avg_rating,
        'num_ratings': num_ratings,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
def user_page(request, username=None):
    template = loader.get_template('streaming/userpage.html')
    if not username:
        username = request.user.username
    user = SiteUser.objects.get(username=username)
    media_history = user.watch_history.watchevent_set.all()
    if request.method == 'POST': #user wants to follow/unfollow
        if 'follow_button' in request.POST:
            if request.POST['follow_button'] == 'Follow':
                request.user.friends.follows.add(user)
            elif request.POST['follow_button'] == 'Unfollow':
                request.user.friends.follows.remove(user)
        elif 'message' in request.POST: #user wants to message
            return messageInbox(request, user)
    history_paginator = Paginator(media_history.order_by('-time_watched'), 5)
    history_page = request.GET.get('page')
    history = history_paginator.get_page(history_page)
    context = {
        'user': user,
        'friends': request.user.friends.follows.filter(username=user.username).exists(),
        'friendsList': user.friends.follows.all(),
        'rating':  Rating.objects.filter(posted_by=user).last(),
        'comments': paginate_comments(request, user.comment_section),
        'history': history,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
def rental_page(request, title):
    template = loader.get_template('streaming/rentPage.html')
    media = get_media(title)
    if not media:
        return HttpResponse("Invalid media")
    if request.method == 'POST':
        rental = Rental.objects.create(siteuser=request.user, movie=media)
        rental.save()
        return HttpResponseRedirect(reverse('streaming:watch_media', kwargs={'title': title}))
    context = {
        'user': request.user,
        'media': media
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
def subscription_page(request, title, season_number, episode_number):
    template = loader.get_template('streaming/subPage.html')
    show = get_media(title)
    if show is None:
        return HttpResponse("BAD MEDIA")
    exceed_subs = len(request.user.subscriptions.all()) >= MAX_SUBS
    print(len(request.user.subscriptions.all()))
    if request.method == 'POST':
        subscription = Subscription.objects.create(siteuser=request.user, show=show)
        subscription.save()
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
@active_user
def unsubscription_page(request, title):
    template = loader.get_template('streaming/unsubPage.html')
    show = get_media(title)
    if show is None:
        return HttpResponse("BAD MEDIA")
    if request.method == 'POST':
        request.user.billing.unsub_list.add(show)
        return HttpResponseRedirect(reverse('streaming:display_media', kwargs={'title': title}))

    context = {
        'user': request.user,
        'show': show,
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
@subscription_required
def watch_media(request, title, season_number=None, episode_number=None):
    template = loader.get_template('streaming/watchMedia.html')
    media = []
    history = request.user.watch_history
    if Movie.objects.filter(title=title).exists():
        media = Movie.objects.get(title=title)
        watch_event = WatchEvent(movie=media, part_of=history)
        watch_event.save()
        movie = True
    if not media:
        show = TVShow.objects.get(title=title)
        movie = False
        media = get_episode(show, season_number, episode_number)
        watch_event = WatchEvent(tv=media, part_of=history)
        watch_event.save()
    context = {
        'media': media,
        'movie': movie
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
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
@active_user
def friends(request):
    template = loader.get_template('streaming/friendPage.html')
    friends = request.user.friends.follows.all()
    context = {
        'friends': friends
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='streaming:login')
@active_user
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
@active_user
def account_page(request):

    #hide the user's sensitive cc information
    billing_cc_num = request.user.billing.cc_num
    cc_num_hidden = ''
    expiration_month = request.user.billing.exp_month
    expiration_year = request.user.billing.exp_year
    cvc_num = request.user.billing.cvc_num

    if billing_cc_num != '': #the user has a cc number on record
        cc_num_hidden ="************" + billing_cc_num[-4:] #returns last 4 digits of the cc_num
    if expiration_month == 0: #the user has a canceled plan or has never entered information
        expiration_month = None
        expiration_year = None
        cvc_num = None

    form = notifications_form()

    context = {
        'form' : form,
        'message' : None,
        'cc_num_hidden': cc_num_hidden,
        'transactions': request.user.billing.transaction_set.all(),
        'expiration_month': expiration_month,
        'expiration_year': expiration_year,
        'cvc_num': cvc_num,
    }

    if request.method == 'POST':
        if 'emailIn' in request.POST:
            request.user.preferences.email_opt_in = True
            context['message'] = "*You are now opted in to email notifications.*\n\n"
        elif 'emailOut' in request.POST:
            request.user.preferences.email_opt_in = False
            if not request.user.preferences.inbox_opt_in: #the user is not subscribed to inbox messages and wishes to opt out of emails
                request.user.preferences.inbox_opt_in = True
                context['message'] = "*You are now opted out of email notifications \nand into inbox notifications.*"
            else:
                context['message'] = "*You are now opted out of email notifications.*\n\n"
        elif 'inboxIn' in request.POST:
            request.user.preferences.inbox_opt_in = True
            context['message'] = "*You are now opted in to inbox notifications.*\n\n"
        elif 'inboxOut' in request.POST:
            request.user.preferences.inbox_opt_in = False
            if not request.user.preferences.email_opt_in: #the user is not subscribed to emails and wishes to opt out of inbox messages
                request.user.preferences.email_opt_in = True
                context['message'] = "*You are now opted out of inbox notifications \nand into email notifications.*"
            else:
                context['message'] = "*You are now opted out of inbox notifications.*\n\n"
        request.user.preferences.save()

    return render(request, 'streaming/accountPage.html', context)


@login_required(login_url='streaming:login')
@active_user
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
                    if (message.__str__() == data['read'] or (data['read'] == "%all%" and not message.read)):
                        message.read = True
                        message.part_of.num_read_messages += 1
                        message.part_of.num_unread_messages -= 1
                        message.save() #save the changes to the Message object
                        message.part_of.save() #save the changes to the Inbox object
                        if not data['read'] == "%all%":
                            break
                return HttpResponseRedirect(reverse('streaming:inbox'))

    context = {
        'form': form,
        'messages_from': messages_from,
    }

    return render(request, 'streaming/inbox.html', context)


@login_required(login_url='streaming:login')
@active_user
def messageInbox(request, sendTo=None):
    form = message_form()
    from_user = request.user

    if sendTo is None:
        sendTo = ''

    # Used for autocomplete of friend names
    friends = request.user.friends.follows.all()

    context = {
        'form' : form,
        'error_message' : None,
        'sendTo': sendTo,
        'friends': friends,
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
@active_user
def sentInbox(request, sendTo=None):
    from_user = request.user
    messages_to = Message.objects.filter(from_user=from_user)  #get all messages the current user has sent to other inbox's

    context = {
        'messages_to' : messages_to
    }

    return render(request, 'streaming/sentInbox.html', context)


@login_required(login_url='streaming:login')
@active_user
def readInbox(request, sendTo=None):
    from_user = request.user
    messages_from = from_user.inbox.message_set.all() #get all of the current user's messages
    context = {
        'messages_from': messages_from,
    }

    return render(request, 'streaming/readInbox.html', context)

@relog_required
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
            now = datetime.now()
            if (data['exp_year'] < now.year) or (data['exp_year'] == now.year and data['exp_month'] < now.month):
                context['error_message'] = "This credit card is expired! Please enter a valid credit card."
            else:
                request.user.billing.name = data['name']
                request.user.billing.cc_num = data['cc_num']
                request.user.billing.cvc_num = data['cvc_num']
                request.user.billing.exp_month = data['exp_month']
                request.user.billing.exp_year = data['exp_year']
                request.user.billing.save()
                if request.user.billing.next_payment_date <= datetime.now().date():
                    package_charge(request.user)

                return redirect('/streaming/account')

    return render(request, 'streaming/billing.html', context)


@login_required(login_url='streaming:login')
def editProfile(request):
    form = profile_form(request.POST)
    if form.is_valid():
        data = form.cleaned_data
        request.user.bio = data['bio']
        request.user.save()

        return HttpResponseRedirect(reverse('streaming:user_page'))

    return render(request, 'streaming/editProfile.html', {'form': form})


@login_required(login_url='streaming:login')
def inactiveAccount(request):
    return render(request, 'streaming/inactiveAccount.html')


@login_required(login_url='streaming:login')
@active_user
def cancel_plan(request):
    request.user.billing.cancel()
    return render(request, 'streaming/accountPage.html')


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
                return render(request, 'streaming/changeInfo.html', context)
            else:
                if len(SiteUser.objects.filter(username=data['username'])) == 1 and data['username'] != request.user.username: #the user entered a username that already exists, and it isn't their current username
                    context['error_message'] = "That user already exists. Please enter a unique username."
                    return render(request, 'streaming/changeInfo.html', context)
                user = request.user
                user.username = data['username']
                user.first_name = data['first_name']
                user.last_name = data['last_name']
                user.email = data['email']
                user.save()

                return render(request, 'streaming/accountPage.html')

    return render(request, 'streaming/changeInfo.html', context)


@login_required(login_url='streaming:login')
def about(request):
    return render(request, 'streaming/about.html')


@login_required(login_url='streaming:login')
def pick_photo(request):
    template = loader.get_template('streaming/profilePhoto.html')
    if request.method == 'POST':
        request.user.profile_picture = '/profile_pictures/' + request.POST.get('image_choice')
        request.user.save()
        return HttpResponseRedirect(reverse('streaming:user_page'))
    photos = listdir('streaming/media/profile_pictures/')
    context = {
        'photos': photos,
    }
    return HttpResponse(template.render(context, request))


def handler400(request):
    return render(request, '404.html', status=404)


def handler500(request):
    return render(request, '500.html', status=500)
