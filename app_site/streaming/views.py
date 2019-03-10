# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from .models import User, Movie, TVShow, Metadata

from django.template import loader

from django.http import HttpResponse, HttpResponseRedirect

from .forms import CreateUser


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


def create_user(request):
    form = CreateUser()
    return render(request, 'streaming/createUser.html', {'form': form})
