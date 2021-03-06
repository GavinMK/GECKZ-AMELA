from django import forms
from streaming.models import Comment


class user_form(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    password = forms.CharField(label='Password', max_length=20)
    first_name = forms.CharField(label='First Name', max_length=20)
    last_name = forms.CharField(label='Last Name', max_length=20)
    email = forms.CharField(label='Email', max_length=30)


class login_form(forms.Form):
    username = forms.CharField(label='Username', max_length=15)
    password = forms.CharField(label='Password', max_length=20)


class search_form(forms.Form):
    request = forms.CharField(label='request', max_length=128)


class message_form(forms.Form):
    username = forms.CharField(label='Username', max_length=15)
    content = forms.CharField(label='Content', max_length=3000)


class mark_message_as_read_form(forms.Form):
    read = forms.CharField(label='Read', max_length=1000)


class billing_form(forms.Form):
    name = forms.CharField(label='Name on Card', max_length=40)
    cc_num = forms.CharField(label='Card Number')
    cvc_num = forms.CharField(label='CVC Number')
    exp_month = forms.IntegerField(label='Expiration Month')
    exp_year = forms.IntegerField(label='Expiration Year')


class change_info(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    old_password = forms.CharField(label='Password', max_length=20)
    new_password = forms.CharField(label='Password', max_length=20, required=False)
    first_name = forms.CharField(label='First Name', max_length=20)
    last_name = forms.CharField(label='Last Name', max_length=20)
    email = forms.CharField(label='Email', max_length=30)


class CommentForm(forms.Form):
    content = forms.CharField(label='Username', max_length=500)
    url = forms.CharField(label='URL', max_length=100)


class profile_form(forms.Form):
    bio = forms.CharField(label='bio')
    #fav_movies = forms.CharField(label='fav_movies')
    #fav_shows = forms.CharField(label='fav_shows')


class notifications_form(forms.Form):
    email_notification = forms.BooleanField(required=False)
    inbox_notification = forms.BooleanField(required=False)
