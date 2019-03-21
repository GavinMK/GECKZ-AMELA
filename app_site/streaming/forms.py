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


class message_form(forms.Form):
    username = forms.CharField(label='Username', max_length=15)
    content = forms.CharField(label='Content', max_length=3000)

#this method is reqiured to retrieve data from a template, although the data will always be True,
#so there need not be an explicit definition of this form
class mark_message_as_read(forms.Form):
    pass


class billing_form(forms.Form):
    name = forms.CharField(label='Name on Card', max_length=40)
    cc_num = forms.IntegerField(label='Card Number')
    cvc_num = forms.IntegerField(label='CVC Number')
    exp_month = forms.IntegerField(label='Expiration Month')
    exp_year = forms.IntegerField(label='Expiration Month')


class change_form(forms.Form):
    username = forms.CharField(label='Username', max_length=20)
    old_password = forms.CharField(label='Password', max_length=20)
    new_password = forms.CharField(label='Password', max_length=20)
    first_name = forms.CharField(label='First Name', max_length=20)
    last_name = forms.CharField(label='Last Name', max_length=20)
    email = forms.CharField(label='Email', max_length=30)
