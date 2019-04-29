from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import TVShow, TVSeason
from django.contrib.auth import logout
from datetime import datetime, timezone

def anonymous_only_redirect(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('streaming:homepage'))
        else:
            return function(request, *args, **kwargs)
    return wrap


def relog_required(function):
    def wrap(request, *args, **kwargs):
        if (datetime.now(timezone.utc) - request.user.last_login).total_seconds() > 300:
            logout(request)
        return function(request, *args, **kwargs)
    return wrap


def subscription_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.subscriptions.filter(title=kwargs['title']).exists() or \
                request.user.rentals.filter(title=kwargs['title']).exists():
            return function(request, *args, **kwargs)
        else:
            if TVShow.objects.filter(title=kwargs['title']).exists():
                return HttpResponseRedirect(reverse('streaming:subscribe', kwargs={'title':kwargs['title'],
                                                    'season_number': kwargs['season_number'], 'episode_number': kwargs['episode_number']}))
            else:
                return HttpResponseRedirect(reverse('streaming:rental', kwargs={'title':kwargs['title']}))
    return wrap


def active_user(function):
    def wrap(request, *args, **kwargs):
        if request.user.billing.next_payment_date > datetime.now().date():
            return function(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('streaming:inactiveAccount'))
    return wrap
