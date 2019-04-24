from .models import *
from .constants import *
from django.db.models import Q
import re
from django.core.paginator import Paginator

from django.core.mail import send_mail
from django.conf import settings


def package_charge(user):
    print("Attempting to charge " + str(user))
    billing = user.billing
    amount = BASE_COST
    if billing.cc_num != 0:
        if len(user.subscriptions.all()) > MAX_SUBS:
            amount = amount + (ADDITIONAL_SUB_COST * (len(user.subscriptions.all()) - MAX_SUBS))
        billing.next_payment_date = datetime.now().date() + timedelta(30)
        for show in billing.unsub_list.all():
            user.subscriptions.remove(show)
            billing.unsub_list.remove(show)
        transaction = Transaction(amount=amount, charged_to=user, part_of=billing, statement='package charge')
        transaction.save()
        billing.save()
        print(str(user) + " has been charged " + str(transaction.amount) + ", next payment date is " + billing.next_payment_date.strftime('%c'))
    else:
        print(str(user) + " has no valid payment info, no charge occurred")


def send_inbox_message(user):
    print("Sending a message to", user.username)
    message_content = 'Dear valued customer, we are writing to inform you that you are awesome. Sincerely, the Amela Development Team.'
    new_message = Message(content=message_content, from_user=SiteUser.objects.get(username="amela"), part_of=user.inbox)
    new_message.save()
    user.inbox.num_messages += 1
    user.inbox.num_unread_messages += 1
    user.inbox.save()


def send_email(user):
    print("Sending an email to", user.username)
    subject = 'Billing Cycle Update for ' + user.username
    message = 'Dear valued customer, we are writing to inform you that you are awesome. Sincerely, the Amela Development Team.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user.email,]
    send_mail(subject, message, email_from, recipient_list)


def rental_charge(user):
    print("Attempting to charge " + str(user))
    billing = user.billing
    if billing.cc_num != 0:
        amount = len(user.rentals.all()) * RENTAL_COST
        user.rentals.clear()
        if amount != 0.0:
            transaction = Transaction(amount=amount, charged_to=user, part_of=billing, statement='rental charge')
            transaction.save()
            billing.save()
            print(str(user) + " has been charged " + str(
                transaction.amount) + ", next payment date is " + billing.next_payment_date.strftime('%c'))
        else:
            print(str(user) + " has no movies")
    else:
        print(str(user) + " has no valid payment info, no charge occurred")


def get_rating(ratings):
    num_ratings = len(ratings)

    avg_rating = 0

    for rating in ratings:
        avg_rating += rating.rating
    if num_ratings > 0:
        avg_rating /= num_ratings

    return avg_rating * 100 / 5, avg_rating


def get_media(title):
    media = None
    if Movie.objects.filter(title=title).exists():
        media = Movie.objects.get(title=title)
    elif TVShow.objects.filter(title=title).exists():
        media = TVShow.objects.get(title=title)
    return media


def get_comment_section(request, url_path):
    url = url_path.replace("%20", " ")
    media_match = re.match(r'.*/media/(?P<media_title>[^/]*)/(?P<season>\d+)?/?(?P<episode>\d+)?', url)
    if media_match:
        title = media_match.group('media_title')
        season_number = media_match.group('season')
        episode_number = media_match.group('episode')
        media = get_media(title)
        if type(media) is TVShow and episode_number is not None:
            episode = get_episode(media, int(season_number), int(episode_number))
            return episode.comment_section
        else:
            return media.comment_section
    else:
        username_grabber = re.match(r'.*/userpage/([^?]*)', url)
        if username_grabber and username_grabber.group(1):
            user = SiteUser.objects.get(username=username_grabber.group(1))
            return user.comment_section
        return request.user.comment_section
    return None


def paginate_comments(request, comment_section):
    comment_paginator = Paginator(comment_section.comment_set.all().order_by('-timestamp'), 5)
    comment_page = request.GET.get('comment_page')
    return comment_paginator.get_page(comment_page)


def get_season(show, season_number):
    season = None
    if show.tvseason_set.filter(season_number=season_number).exists():
        season = show.tvseason_set.get(season_number=season_number)
    return season


def get_episode(show, season_number, episode_number):
    episode = None
    season = get_season(show, season_number)
    if season is not None and season.tvepisode_set.filter(episode_number=episode_number).exists():
        episode = season.tvepisode_set.get(episode_number=episode_number)
    return episode

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
    friends = Friend()
    friends.save()
    return SiteUser.objects.create_user(data['username'], email=data['email'], password=data['password'],
                                        first_name=data['first_name'], last_name=data['last_name'],
                                        preferences=preferences, comment_section=comment_section,
                                        inbox=inbox, billing=billing, watch_history=history, friends=friends)


def filter_db_query(context, tv_show_list, movie_list):

    tv_results = tv_show_list
    movie_results = movie_list
    # We go through each word in the query, and check to make sure it matches at least some of the data
    # Each result has to match all of the words.
    for search_filter in context['filters']:
        # Filters that don't have a value don't need to be checked!
        if search_filter.value != "":
            words = search_filter.value.split(" ")
            for word in words:
                print(word)
                db_query = Q()
                if search_filter.name == 'Title':
                    db_query |= Q(title__icontains=word)
                elif search_filter.name == 'Genre':
                    db_query |= Q(metadata__genre__icontains=word)
                elif search_filter.name == 'Release Year':
                    db_query |= Q(metadata__release_year__icontains=word)
                elif search_filter.name == 'Studio':
                    db_query |= Q(metadata__studio__icontains=word)
                elif search_filter.name == 'Streaming Service':
                    db_query |= Q(metadata__streaming_service__icontains=word)
                elif search_filter.name == 'Actors':
                    db_query |= Q(metadata__actor__name__icontains=word)
                else:
                    raise TypeError("Search filter '{0}' is not a recognized filter!".format(search_filter.name))
                partial_tv_results = tv_show_list.filter(db_query)
                partial_movie_results = movie_list.filter(db_query)
                tv_results &= partial_tv_results
                movie_results &= partial_movie_results
    return tuple(set(tv_results) | set(movie_results))
