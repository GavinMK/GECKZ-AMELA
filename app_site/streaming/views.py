# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponseRedirect

from django.urls import reverse

from datetime import datetime

from django.shortcuts import render


from .models import User, Movie, TVShow, Metadata, Preferences, CommentSection, Inbox, Billing

from django.db import models

from django.utils import timezone

from django.template import loader

from django.http import HttpResponse, HttpResponseRedirect

from .forms import user_form, login_form


def validate_password(password_candidate):
    valid = False
    if len(password_candidate) > 7:
        if any(char.isdigit()for char in password_candidate):
            valid = any(char.isupper() for char in password_candidate)
    return valid


def hash_password(password):
    #TODO actually hash the password
    return password


def generate_user(data):
    username = data['username']
    first_name = data['first_name']
    last_name = data['last_name']
    password = data['password']
    email = data['email']
    password = hash_password(password)
    # May need to figure out how to do it with the foreign keys
    preferences = Preferences()
    preferences.save()
    comment_section = CommentSection()
    comment_section.save()
    inbox = Inbox()
    inbox.save()
    billing = Billing()
    billing.save()
    return User(username=username, first_name=first_name, last_name=last_name, password=password,
                 email=email,
                 last_login=datetime.now(), preferences=preferences, comment_section=comment_section,
                 inbox=inbox, billing=billing)


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

def create_user_page(request):
    template = loader.get_template('streaming/createUser.html')
    form = user_form()
    context = {
        'form': form,
        'error_message': ''
    }
    if request.method == 'POST':
        form = user_form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                User.objects.get(username=data['username'])
                context['error_message'] = "That username is taken"
            except (KeyError, User.DoesNotExist):
                if validate_password(data['password']):
                    generate_user(data).save()
                    return HttpResponseRedirect(reverse('streaming:index'))
                else:
                    print("bad pass")
                    context['error_message'] = "That password is invalid"
    print('render new')
    return HttpResponse(template.render(context, request))


def login(request):
    form = login_form()
    return render(request, 'streaming/login.html', {'form': form})
