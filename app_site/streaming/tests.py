# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, Client
from django.apps import apps

from .views import *
from .util import *
from .models import *

from datetime import *

class SimpleTest(TestCase):

    def create_test_user(self):
        user_info = {
            'username': 'test123',
            'email': 'test213@23.com',
            'password': 'test',
            'first_name': 'first',
            'last_name': 'last',
        }
        user = generate_user(user_info)
        return user

    def populate_billing(self, user):
        user.billing.cc_num = '1234123412341234'
        user.billing.cvc_num = 123
        user.billing.name = 'test user'
        user.billing.change_date()
        user.save()

    def get_user(self):
        user = None
        potential_user = SiteUser.objects.filter(username='test123')
        if len(potential_user) == 1:
            user = potential_user[0]
        else:
            user = self.create_test_user()
        user.last_login = datetime.now()
        return user

    def setUp(self):
        # Every test needs access to the request factory.
        self.factory = RequestFactory()
        self.c = Client()
        #self.c.login(username='test123', password='test')



    def test_views(self):
        self.generic_test('create user page', self.factory.get('/streaming/createUser/'), AnonymousUser(), create_user_page, 200)
        #self.generic_test('login', self.factory.post('/streaming/login/', {'username': 'test123', 'password':'test'}), AnonymousUser(), login_page, 200)
        response = self.c.post('/streaming/createuser/', {'username': 'test123', 'password':'test', 'email': 'test213@23.com', 'first_name': 'first', 'last_name': 'last'})
        response = self.c.post('/streaming/login/?next=/streaming/', {'username':'test123', 'password': 'test'})
        self.c.login(username='test123', password='test')
        self.c.get('/streaming/logout/')
        #self.generic_test('logout', self.factory.get('/streaming/login/'), self.get_user(), logout_requested, 200) #breaks becuase not actually logged in
        self.generic_test('redirect homepage', self.factory.get('/streaming/homepage/'), self.get_user(), redirect_homepage, 302)
        self.generic_test('search', self.factory.get('/streaming/search/?Title=test&Genre=test&Release+Year=test&Studio=test&Streaming+Service=test&Actors=test'), self.get_user(), search, 200)
        self.generic_test('userpage', self.factory.get('/streaming/userpage/'), self.get_user(), user_page, 200)
        self.generic_test('user search', self.factory.get('/streaming/userSearchPage/'), self.get_user(), user_search, 200)
        self.generic_test('movies', self.factory.get('/streaming/mediaList/'), self.get_user(), movies, 200)
        self.generic_test('shows', self.factory.get('/streaming/mediaList/'), self.get_user(), shows, 200)
        self.generic_test('post comment', self.factory.post('/streaming/userpage/', {'url':'/streaming/userpage/', 'content':'test, might delete later'}), self.get_user(), post_comment, 302)
        self.generic_test('display media', self.factory.get('/streaming/mediaDisplay/'), self.get_user(), display_media, 200, ['Bonanza'])
        self.generic_test('display episode', self.factory.get('/streaming/tvEpsisode/'), self.get_user(), display_episode, 200, ['Bonanza', '1', '29'])
        self.generic_test('rental', self.factory.get('/streaming/rentPage/'), self.get_user(), rental_page, 200, ['Frankenstein'])
        self.generic_test('subscription page', self.factory.get('/streaming/subPage/'), self.get_user(), subscription_page, 200, ['Bonanza', '1', '29'])
        self.generic_test('unsubscription page', self.factory.get('/streaming/unsubPage/'), self.get_user(), unsubscription_page, 200, ['Bonanza'])
        user = self.get_user()
        subscription = Subscription.objects.create(siteuser=user, show=get_media('Bonanza'))
        subscription.save()
        s = SearchFilter('Title', self.factory.get('/streaming/search/?Title=test&Genre=test&Release+Year=test&Studio=test&Streaming+Service=test&Actors=test'), ())
        str(s)
        self.generic_test('watch media', self.factory.get('/streaming/watchMedia/'), user, watch_media, 200, None, {'title':'Bonanza', 'season_number':'1', 'episode_number':'29'}) #TODO look into this not working
        #post request for post comments here
        self.generic_test('post rating', self.factory.post('/streaming/media/Bonanza/1/29/', {'url':'http://127.0.0.1:8000/streaming/media/Bonanza/1/29/', 'rating':'5'}), self.get_user(), post_rating, 302)
        self.generic_test('friends', self.factory.get('/streaming/friendPage/'), self.get_user(), friends, 200)
        self.generic_test('homepage', self.factory.get('/streaming/homepage/'), self.get_user(), homepage, 200)
        self.generic_test('account page', self.factory.post('/streaming/accountPage/', {'inboxOut': ''}), self.get_user(), account_page, 200)
        self.generic_test('inbox', self.factory.get('/streaming/inbox/'), self.get_user(), inbox, 200)
        self.generic_test('message inbox', self.factory.get('/streaming/messageInbox/'), self.get_user(), messageInbox, 200)
        self.generic_test('sent inbox', self.factory.get('/streaming/sentInbox/'), self.get_user(), sentInbox, 200)
        self.generic_test('read inbox', self.factory.get('/streaming/readInbox/'), self.get_user(), readInbox, 200)

        #self.generic_test('billing', self.factory.get('/streaming/billing/'), self.get_user(), billing, 200) #broken due to last login
        self.c.login(username='test123', password='test')
        self.c.post('/streaming/billing/', {'name': 'test123', 'cc_num':'1234123412341234', 'cvc_num': '123', 'exp_month':'12', 'exp_year':'2020'})

        self.generic_test('edit profile', self.factory.post('/streaming/editProfile/', {'bio': 'testing1234'}), self.get_user(), editProfile, 302) #better as post
        self.generic_test('inactive account', self.factory.get('/streaming/inactiveAccount/'), self.get_user(), inactiveAccount, 200)
        self.generic_test('cancel plan', self.factory.get('/streaming/accountPage/'), self.get_user(), cancel_plan, 200)
        self.generic_test('change', self.factory.post('/streaming/changeInfo/', {'old_password': 'test', 'username': 'test123', 'email': 'test213@23.com', 'first_name': 'first', 'last_name': 'last'}), self.get_user(), change, 200)
        self.generic_test('about', self.factory.get('/streaming/about/'), self.get_user(), about, 200)
        self.generic_test('profile upload', self.factory.get('/streaming/profilePicture/'), self.get_user(), profile_upload, 200) #used? if so POST
        self.generic_test('pick photo', self.factory.post('/streaming/profilePhoto/', {'image_choice':'mad.png'}), self.get_user(), pick_photo, 302)


    def test_utils(self):
        user = self.get_user()
        self.populate_billing(user)
        package_charge(user)
        send_inbox_message(user)
        send_email(user)
        r = Rental(siteuser=user, movie=get_media('Frankenstein'), duration=-50)
        r.save()
        rental_charge(user)
        get_comment_section(self.factory.get('/streaming/media/Bonanza/1/29/'), '/streaming/media/Bonanza/1/29/')
        validate_password('asdfASFAE214$#@!')
        user_info = {
            'username': 'abcdefg',
            'email': 'test213@23.com',
            'password': 'test',
            'first_name': 'first',
            'last_name': 'last',
        }
        user1 = generate_user(user_info)
        user1.delete()

    def test_models(self):
        for name, model in apps.all_models['streaming'].items():
            print('Testing', name, 'to string')
            for item in model.objects.all():
                str(item)




    def generic_test(self, element, request, user, view, status_code, args=None, kwargs=None):
        #print("Testing", element)
        request.user = user
        if not args and not kwargs:
            response = view(request)
        elif args:
            response = view(request, *args)
        elif kwargs:
            response = view(request, **kwargs)
        self.assertEqual(response.status_code, status_code)


#test
