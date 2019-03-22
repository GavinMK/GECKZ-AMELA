from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import TVShow, TVSeason


def anonymous_only_redirect(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('streaming:homepage'))
        else:
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

