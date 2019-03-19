from django import forms


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


class billing_form(forms.Form):
    name = forms.CharField(label='Name on Card', max_length=40)
    cc_num = forms.IntegerField(label='Card Number')
    cvc_num = forms.IntegerField(label='CVC Number')
    exp_date = forms.DateField(label='Expiration Date', widget=forms.SelectDateWidget)
