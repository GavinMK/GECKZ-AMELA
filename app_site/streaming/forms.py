from django import forms


class CreateUser(forms.Form):
    username = forms.CharField(label='Username', max_length=15)
    password = forms.CharField(label='Password', max_length=20)
    first_name = forms.CharField(label='First Name', max_length=20)
    last_name = forms.CharField(label='Last Name', max_length=20)
    email = forms.CharField(label='Email', max_length=30)
