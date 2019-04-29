# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import AnonymousUser, User
from django.test import RequestFactory, TestCase, Client

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
        user.billing.cc_num = '1234123412341234'
        user.billing.cvc_num = 123
        user.billing.name = 'test user'
        user.billing.change_date()
        return user


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


    def test_userpage(self):
        print("Testing userpage")
        # Create an instance of a GET request.
        request = self.factory.get('/streaming/userpage/')

        # Recall that middleware are not supported. You can simulate a
        # logged-in user by setting request.user manually.
        request.user = self.get_user()

        # Or you can simulate an anonymous user by setting request.user to
        # an AnonymousUser instance.
        #request.user = AnonymousUser()

        # Test my_view() as if it were deployed at /customer/details
        response = user_page(request)
        # Use this syntax for class-based views.
        self.assertEqual(response.status_code, 200)


    '''def test_logout(self):
        print("Testing logout")
        request = self.factory.get('/streaming/homepage/')
        request.user = self.get_user()
        response = logout_requested(request)
        self.assertEqual(response.status_code, 200)'''

    def test_movies(self):
        pass

    def test_show(self):
        pass


    def test_generic_test(self):
        self.generic_test('create user page', self.factory.get('/streaming/createUser/'), AnonymousUser(), create_user_page, 200)
        self.generic_test('login', self.factory.get('/streaming/login/'), AnonymousUser(), login_page, 200)
        #self.generic_test('logout', self.factory.get('/streaming/login/'), self.get_user(), logout_requested, 200) #breaks becuase not actually logged in
        self.generic_test('redirect homepage', self.factory.get('/streaming/homepage/'), self.get_user(), redirect_homepage, 302)
        self.generic_test('search', self.factory.get('/streaming/searchPage/'), self.get_user(), search, 200)
        self.generic_test('user search', self.factory.get('/streaming/userSearchPage/'), self.get_user(), user_search, 200)
        self.generic_test('movies', self.factory.get('/streaming/mediaList/'), self.get_user(), movies, 200)
        self.generic_test('shows', self.factory.get('/streaming/mediaList/'), self.get_user(), shows, 200)
        self.generic_test('post comment', self.factory.get('/streaming/userpage/'), self.get_user(), post_comment, 302)
        self.generic_test('display media', self.factory.get('/streaming/mediaDisplay/'), self.get_user(), display_media, 200, ['Bonanza'])
        self.generic_test('display episode', self.factory.get('/streaming/tvEpsisode/'), self.get_user(), display_episode, 200, ['Bonanza', '1', '29'])
        self.generic_test('rental', self.factory.get('/streaming/rentPage/'), self.get_user(), rental_page, 200, ['Frankenstein'])
        self.generic_test('subscription page', self.factory.get('/streaming/subPage/'), self.get_user(), subscription_page, 200, ['Bonanza', '1', '29'])
        self.generic_test('unsubscription page', self.factory.get('/streaming/unsubPage/'), self.get_user(), unsubscription_page, 200, ['Bonanza'])
        #user = self.get_user()
        #subscription = Subscription.objects.create(siteuser=user, show=get_media('Bonanza'))
        #subscription.save()
        #self.generic_test('watch media', self.factory.get('/streaming/watchMedia/'), user, watch_media, 200, ['Frankenstein']) #TODO look into this not working
        #post request for post comments here
        self.generic_test('friends', self.factory.get('/streaming/friendPage/'), self.get_user(), friends, 200)
        self.generic_test('homepage', self.factory.get('/streaming/homepage/'), self.get_user(), homepage, 200)
        self.generic_test('account page', self.factory.get('/streaming/accountPage/'), self.get_user(), account_page, 200)
        self.generic_test('inbox', self.factory.get('/streaming/inbox/'), self.get_user(), inbox, 200)
        self.generic_test('message inbox', self.factory.get('/streaming/messageInbox/'), self.get_user(), messageInbox, 200)
        self.generic_test('sent inbox', self.factory.get('/streaming/sentInbox/'), self.get_user(), sentInbox, 200)
        self.generic_test('read inbox', self.factory.get('/streaming/readInbox/'), self.get_user(), readInbox, 200)
        #self.generic_test('billing', self.factory.get('/streaming/billing/'), self.get_user(), billing, 200) #broken due to last login
        self.generic_test('edit profile', self.factory.get('/streaming/editProfile/'), self.get_user(), editProfile, 200) #better as post
        self.generic_test('inactive account', self.factory.get('/streaming/inactiveAccount/'), self.get_user(), inactiveAccount, 200)
        self.generic_test('cancel plan', self.factory.get('/streaming/accountPage/'), self.get_user(), cancel_plan, 200)
        self.generic_test('change', self.factory.get('/streaming/changeInfo/'), self.get_user(), change, 200) #better as POST
        self.generic_test('about', self.factory.get('/streaming/about/'), self.get_user(), about, 200)
        self.generic_test('profile upload', self.factory.get('/streaming/profilePicture/'), self.get_user(), profile_upload, 200) #used? if so POST
        self.generic_test('pick photo', self.factory.get('/streaming/profilePhoto/'), self.get_user(), pick_photo, 200)





    def generic_test(self, element, request, user, view, status_code, args=None):
        print("Testing", element)
        request.user = user
        if not args:
            response = view(request)
        else:
            response = view(request, *args)
        self.assertEqual(response.status_code, status_code)


#test
