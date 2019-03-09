# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from streaming.models import User, Movie, TVShow, Metadata

from django.template import loader

from django.http import HttpResponse


def index(request):
    template = loader.get_template('streaming/index.html')
    context = {
        'objects': User.objects.values(),
        'movie': Movie.objects.values(),
        'show': TVShow.objects.values(),
        'meta': Metadata.objects.values(),
        'pokemon': Movie.objects.filter(title='Pokemon')
    }
    return HttpResponse(template.render(context, request))

def authenticate(request):
    entered_username = request.POST.get('username')
    entered_password = request.POST.get('password')
    user_query = User.objects.filter(username = entered_username)
    if len(user_query) != 1:
        return HttpResponse("Wrong username")
    else:
        if user_query[0].password == entered_password:
            HttpResponseRedirect(reverse('index'))
        return HttpResponse("Wrong password")
