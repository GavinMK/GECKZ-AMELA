# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from django.shortcuts import render


from streaming.models import User, Movie, TVShow, Metadata, Preferences, CommentSection, Inbox, Billing

from django.db import models

from django.utils import timezone

from django.template import loader

from django.http import HttpResponse, HttpResponseRedirect

from .forms import CreateUser


def validate_password(password_candidate):
    valid = False
    if len(password_candidate) > 7:
        if any(char.isdigit()for char in password_candidate):
            valid = any(char.isupper() for char in password_candidate)
    return valid


def hash_password(password):
    #TODO actually hash the password
    return password


def create_user(request):
    # Template must have inputs with ids matching those in the post gets.
    username = request.POST.get('enteredUser')
    first_name = request.POST.get('enteredName')
    last_name = request.POST.get('enteredLast')
    password = request.POST.get('enteredPass')
    email = request.POST.get('enteredEmail')
    try:
        User.objects.get(username)
    except (KeyError, User.DoesNotExist):
        if validate_password(password):
            password = hash_password(password)
            # May need to figure out how to do it with the foreign keys
            preferences = Preferences()
            comment_section = CommentSection()
            inbox = Inbox()
            billing = Billing()
            model = User(username=username, first_name=first_name, last_name=last_name, password=password, email=email,
                         last_login=timezone.now, preferences=preferences, comment_section=comment_section,
                         inbox=inbox, billing=billing)
            model.save()
            return HttpResponseRedirect(request, 'WHEREVER IT REDIRECTS TO')
    else:
        context = {
            'error_message': "That user already exists!"
        }
        return render(request, "WHEREVER IT REDIRECTS TO", context)


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
