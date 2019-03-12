from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.urls import reverse


def anonymous_only_redirect(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('streaming:homepage'))
        else:
            return function(request, *args, **kwargs)
    return wrap
