# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

from streaming.models import Guy

from django.template import loader

from django.http import HttpResponse


def index(request):
    template = loader.get_template('streaming/index.html')
    context = {
        'objects': Guy.objects.all(),
    }
    return HttpResponse(template.render(context, request))
