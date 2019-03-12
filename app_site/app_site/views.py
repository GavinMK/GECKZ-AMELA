#This file redirects our site-wide homepage to an app directory(currently /streaming/)
#Thus, it does not belong in an app such as streaming

from django.http import HttpResponsePermanentRedirect

def redirect_root(request):
    return HttpResponsePermanentRedirect('/streaming/', permanent=True) #permanent redirect