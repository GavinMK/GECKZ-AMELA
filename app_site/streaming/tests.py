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

    def create_subscription(self, user):
        if not Subscription.objects.filter(siteuser=user):
            subscription = Subscription.objects.create(siteuser=user, show=get_media('Bonanza'))
            subscription.save()
        return user

    def manage_subs(self, user):
        for sub in Subscription.objects.filter(siteuser=user):
            print("deleteing")
            sub.delete()

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
        self.user_creation_test()
        self.login_test()
        #self.generic_test('logout', self.factory.get('/streaming/login/'), self.get_user(), logout_requested, 200) #breaks becuase not actually logged in
        self.generic_test('redirect homepage', self.factory.get('/streaming/homepage/'), self.get_user(), redirect_homepage, 302)
        self.generic_test('search', self.factory.get('/streaming/search/?Title=test&Genre=test&Release+Year=test&Studio=test&Streaming+Service=test&Actors=test'), self.get_user(), search, 200) #valid search with all
        self.generic_test('search', self.factory.get('/streaming/search/?Title='), self.get_user(), search, 200) #valid search with just title
        self.generic_test('search', self.factory.get('/streaming/search/?Qitles=123'), self.get_user(), search, 200) #invalid search

        self.generic_test('user search', self.factory.get('/streaming/usersearch/?q=test'), self.get_user(), user_search, 200)
        self.generic_test('user search', self.factory.get('/streaming/usersearch/'), self.get_user(), user_search, 200)
        self.generic_test('movies', self.factory.get('/streaming/mediaList/'), self.get_user(), movies, 200)
        self.generic_test('shows', self.factory.get('/streaming/mediaList/'), self.get_user(), shows, 200)

        self.display_media()
        self.comment_test()
        self.user_page_test()
        self.subs()
        self.watchmedia()
        self.rating()
        self.billing()
        self.change_test()

        self.generic_test('friends', self.factory.get('/streaming/friendPage/'), self.get_user(), friends, 200)
        self.generic_test('homepage', self.factory.get('/streaming/homepage/'), self.get_user(), homepage, 200)

        self.generic_test('edit profile', self.factory.post('/streaming/editProfile/', {'bio': 'testing1234'}), self.get_user(), editProfile, 302) #valid test
        self.generic_test('edit profile', self.factory.post('/streaming/editProfile/', {'io': 'testing1234'}), self.get_user(), editProfile, 200) #testing invalid post

        self.generic_test('inactive account', self.factory.get('/streaming/inactiveAccount/'), self.get_user(), inactiveAccount, 200)
        self.generic_test('cancel plan', self.factory.get('/streaming/accountPage/'), self.get_user(), cancel_plan, 200)

        self.generic_test('about', self.factory.get('/streaming/about/'), self.get_user(), about, 200)

        self.generic_test('pick photo', self.factory.post('/streaming/profilePhoto/', {'image_choice':'mad.png'}), self.get_user(), pick_photo, 302) #change photo
        self.generic_test('pick photo', self.factory.get('/streaming/profilePhoto/'), self.get_user(), pick_photo, 200) # don't change photo


        self.notification_prefs()
        self.messaging()


    def comment_test(self):
        self.generic_test('post comment', self.factory.get('/streaming/userpage/'), self.get_user(), post_comment, 302) #get request
        self.generic_test('post comment', self.factory.post('/streaming/userpage/', {'url':'/streaming/userpage/', 'content':'test, might delete later'}), self.get_user(), post_comment, 302) #post with successful comment on own userpage
        self.generic_test('post comment', self.factory.post('/streaming/userpage/', {'url':'/streaming/userpage/', 'content':'test, might delete later'*500}), self.get_user(), post_comment, 302) #post with comment too long
        self.generic_test('post comment', self.factory.post('/streaming/friends/GavinDaGOAT', {'url':'/streaming/friends/GavinDaGOAT', 'content':'test, might delete later'}), self.get_user(), post_comment, 302) #post with successful comment on friend page
        self.generic_test('post comment', self.factory.post('/streaming/media/Frankenstein/', {'url':'/streaming/media/Frankenstein/', 'content':'test, might delete later'}), self.get_user(), post_comment, 302) #post with successful comment on media page



    def user_creation_test(self):
        self.generic_test('create user page', self.factory.get('/streaming/createUser/'), AnonymousUser(), create_user_page, 200)
        response = self.c.post('/streaming/createuser/', {'1': 1}) #invalid form
        response = self.c.post('/streaming/createuser/', {'username': 'test1234', 'password':'test', 'email': 'test213@23.com', 'first_name': 'first', 'last_name': 'last'}) #create new
        response = self.c.post('/streaming/createuser/', {'username': 'test1234', 'password':'test', 'email': 'test213@23.com', 'first_name': 'first', 'last_name': 'last'}) #test already exists
        delObj = SiteUser.objects.get(username='test1234')
        delObj.delete()


    def login_test(self):
        self.c.get('/streaming/login/?next=/streaming/') #get request
        self.c.put('/streaming/login/?next=/streaming/') #put request (tests elif at end)
        self.c.post('/streaming/login/?next=/streaming/', {'1': 1}) #post with invalid form
        self.c.post('/streaming/login/?next=/streaming/', {'username':'test123', 'password': 'wrong'}) #post with wrong password
        self.c.post('/streaming/login/?next=/streaming/', {'username':'test123', 'password': 'test', 'redirect': 'None'}) #post, right pw, no redirect
        self.c.logout()
        self.c.post('/streaming/login/?next=/streaming/', {'username':'test123', 'password': 'test'}) #successful post login
        self.c.login(username='test123', password='test') #login with client
        self.c.get('/streaming/logout/') #test logout view (requires client logged in)


    def user_page_test(self):
        self.generic_test('userpage', self.factory.get('/streaming/userpage/'), self.get_user(), user_page, 200)
        self.generic_test('userpage', self.factory.post('/streaming/userpage/', {'follow_button': 'Follow'}), self.get_user(), user_page, 200) #follow
        self.generic_test('userpage', self.factory.post('/streaming/userpage/', {'follow_button': 'Unfollow'}), self.get_user(), user_page, 200) #unfollow
        self.generic_test('userpage', self.factory.post('/streaming/userpage/', {'follow_button': 'no'}), self.get_user(), user_page, 200) #branch
        self.generic_test('userpage', self.factory.post('/streaming/userpage/', {}), self.get_user(), user_page, 200) #empty post
        self.generic_test('userpage', self.factory.post('/streaming/userpage/', {'message': ''}), self.get_user(), user_page, 200)
        self.generic_test('userpage', self.factory.post('/streaming/userpage/', {'message': ''}), self.get_user(), user_page, 200, ['z-ach'])


    def change_test(self):
        self.generic_test('change', self.factory.post('/streaming/changeInfo/', {'old_password': 'test', 'username': 'test123', 'email': 'test213@23.com', 'first_name': 'first', 'last_name': 'last'}), self.get_user(), change, 200) #valid pw
        self.generic_test('change', self.factory.post('/streaming/changeInfo/', {'old_password': 'invalid', 'username': 'test123', 'email': 'test213@23.com', 'first_name': 'first', 'last_name': 'last'}), self.get_user(), change, 200) #invalid pw
        self.generic_test('change', self.factory.get('/streaming/changeInfo/'), self.get_user(), change, 200) #get request
        self.generic_test('change', self.factory.post('/streaming/changeInfo/', {'old_password': 'test'}), self.get_user(), change, 200) #invalid form


    def notification_prefs(self):
        user = self.get_user()
        self.generic_test('account page', self.factory.get('/streaming/accountPage/'), user, account_page, 200)
        self.populate_billing(user)
        for key in ['emailIn', 'inboxIn', 'emailOut', 'emailIn', 'inboxOut', 'emailOut', 'inboxOut', 'asdf']:
            self.generic_test('account page', self.factory.post('/streaming/accountPage/', {key: ''}), user, account_page, 200)


    def messaging(self):
        self.generic_test('message inbox', self.factory.post('/streaming/messageInbox/', {'send': '', 'username': 'z-ach', 'content': 'hi!'}), self.get_user(), messageInbox, 302)
        self.generic_test('message inbox send to self', self.factory.post('/streaming/messageInbox/', {'send': '', 'username': 'test123', 'content': 'hi!'}), self.get_user(), messageInbox, 200)
        self.generic_test('message inbox invalid user', self.factory.post('/streaming/messageInbox/', {'send': '', 'username': 'asfasfewa', 'content': 'hi!'}), self.get_user(), messageInbox, 200)
        self.generic_test('message inbox invalid user', self.factory.post('/streaming/messageInbox/', {'send': 1}), self.get_user(), messageInbox, 200) #form invalid TODO form invalid messageInbox
        self.generic_test('message inbox invalid user', self.factory.get('/streaming/messageInbox/'), self.get_user(), messageInbox, 200) #get request

        message = Message.objects.filter(from_user=SiteUser.objects.get(username='amela'), part_of=self.get_user().inbox)[0]

        self.generic_test('inbox', self.factory.post('/streaming/inbox/', {'read': message}), self.get_user(), inbox, 302) #trigger post set read message
        self.generic_test('inbox', self.factory.post('/streaming/inbox/', {'read': 1}), self.get_user(), inbox, 200) #post but invalid read
        self.generic_test('inbox', self.factory.post('/streaming/inbox/', {'read': False, '1': None}), self.get_user(), inbox, 200) #post invalid form
        self.generic_test('inbox', self.factory.post('/streaming/inbox/', {'': None}), self.get_user(), inbox, 200) #post invalid form
        self.generic_test('inbox', self.factory.get('/streaming/inbox/'), self.get_user(), inbox, 200) #trigger get

        self.generic_test('sent inbox', self.factory.get('/streaming/sentInbox/'), self.get_user(), sentInbox, 200)
        self.generic_test('read inbox', self.factory.get('/streaming/readInbox/'), self.get_user(), readInbox, 200)


    def billing(self):
        self.c.login(username='test123', password='test')
        self.c.post('/streaming/billing/', {'name': 'test123', 'cc_num':'1234123412341234', 'cvc_num': '123', 'exp_month':'12', 'exp_year':'2000'}) #invalid cc year
        self.c.post('/streaming/billing/', {'name': 'test123'}) #invalid form
        self.c.get('/streaming/billing/') #get request
        self.c.post('/streaming/billing/', {'name': 'test123', 'cc_num':'1234123412341234', 'cvc_num': '123', 'exp_month':'12', 'exp_year':'2020'}) #valid with old billing date

        user = SiteUser.objects.get(username='test123')
        user.billing.next_payment_date = datetime.now() - timedelta(days=2)
        user.billing.save()
        self.c.post('/streaming/billing/', {'name': 'test123', 'cc_num':'1234123412341234', 'cvc_num': '123', 'exp_month':'12', 'exp_year':'2020'}) #valid


    def rating(self):
        ratings = Rating.objects.filter(posted_by=self.get_user())
        if ratings:
            for rating in ratings:
                rating.delete()
        self.generic_test('post rating', self.factory.post('/streaming/media/Bonanza/1/29/', {'url':'http://127.0.0.1:8000/streaming/media/Bonanza/1/29/', 'rating':'5'}), self.get_user(), post_rating, 302) #test post rating
        self.generic_test('post rating', self.factory.post('/streaming/media/Bonanza/1/29/', {'url':'http://127.0.0.1:8000/streaming/media/Bonanza/1/29/', 'rating':'4'}), self.get_user(), post_rating, 302) #test change rating
        self.generic_test('post rating', self.factory.post('/streaming/media/Bonanza/1/29/', {'url':'http://127.0.0.1:8000/streaming/media/Bonanza/', 'rating':'6'}), self.get_user(), post_rating, 200) #test invalid rating
        self.generic_test('post rating', self.factory.get('/streaming/media/Bonanza/1/29/'), self.get_user(), post_rating, 302) #test get request


    def display_media(self):
        self.generic_test('display media', self.factory.get('/streaming/mediaDisplay/'), self.get_user(), display_media, 200, ['Bonanza']) #get display media with tv show
        self.generic_test('display media', self.factory.get('/streaming/mediaDisplay/'), self.get_user(), display_media, 200, ['Frankenstein']) #get display media with movie
        self.generic_test('display episode', self.factory.get('/streaming/tvEpsisode/'), self.get_user(), display_episode, 200, ['Bonanza', '1', '29']) #get display tv episode

    def watchmedia(self):
        self.generic_test('watch tv', self.factory.get('/streaming/watchMedia/'), self.get_user(), watch_media, 302, None, {'title':'asfas', 'season_number':'1', 'episode_number':'2'}) #try to view with invalid show
        self.generic_test('watch tv', self.factory.get('/streaming/watchMedia/'), self.get_user(), watch_media, 302, None, {'title':'Medic', 'season_number':'1', 'episode_number':'2'}) #try to view with no subscription
        user = self.create_subscription(self.get_user())
        self.generic_test('watch tv', self.factory.get('/streaming/watchMedia/'), user, watch_media, 200, None, {'title':'Bonanza', 'season_number':'1', 'episode_number':'29'}) #valid
        r = Rental(siteuser=user, movie=get_media('Frankenstein'), duration=-50)
        r.save()
        self.generic_test('watch movie', self.factory.get('/streaming/watchMedia/'), user, watch_media, 200, None, {'title':'Frankenstein'})


    def subs(self):
        self.manage_subs(self.get_user())
        self.generic_test('subscription page', self.factory.get('/streaming/subPage/'), self.get_user(), subscription_page, 200, ['Bonanza', '1', '29'])
        self.generic_test('unsubscription page', self.factory.get('/streaming/unsubPage/'), self.get_user(), unsubscription_page, 200, ['Bonanza'])
        self.generic_test('subscription page', self.factory.post('/streaming/subPage/'), self.get_user(), subscription_page, 302, ['Bonanza', '1', '29'])
        self.generic_test('unsubscription page', self.factory.post('/streaming/unsubPage/'), self.get_user(), unsubscription_page, 302, ['Bonanza'])
        self.generic_test('subscription page', self.factory.get('/streaming/subPage/'), self.get_user(), subscription_page, 200, ['bad', '1', '29'])
        self.generic_test('unsubscription page', self.factory.get('/streaming/unsubPage/'), self.get_user(), unsubscription_page, 200, ['bad'])

        self.generic_test('rental', self.factory.get('/streaming/rentPage/'), self.get_user(), rental_page, 200, ['Frankenstein'])
        self.generic_test('rental', self.factory.get('/streaming/rentPage/'), self.get_user(), rental_page, 200, ['F'])
        self.generic_test('rental', self.factory.post('/streaming/rentPage/'), self.get_user(), rental_page, 302, ['Frankenstein'])


    def test_utils(self):
        user = self.get_user()
        self.util_test_billing()
        send_inbox_message(user)
        send_email(user)
        get_comment_section(self.factory.get('/streaming/media/Bonanza/1/29/'), '/streaming/media/Bonanza/1/29/') #get media comment section
        get_comment_section(self.factory.get('/streaming/userpage/'), '') #get invalid comment section
        media = get_media('Bonanza') #get valid media
        get_season(media, '1') #get valid season
        get_season(media, '10') #get invalid season
        get_episode(media, '1', '-1') #get invalid episode
        get_episode(media, '1', '29') #get valid episode
        get_episode(media, None, '29') #pass invalid season
        validate_password('asdfASFAE214$#@!') #valid password
        validate_password('asdfASFAE$#@!') #invalid password no numbers
        validate_password('1') #invalid password too short
        validate_password('1'*10) #invalid password no chars
        user_info = {
            'username': 'abcdefg',
            'email': 'test213@23.com',
            'password': 'test',
            'first_name': 'first',
            'last_name': 'last',
        }
        user1 = generate_user(user_info)
        user1.delete()
        try:
            s = SearchFilter('a', self.factory.get('/streaming/search/?a=test&Genre=test&Release+Year=test&Studio=test&Streaming+Service=test&Actors=test'), ())
            str(s)
            context = {'filters': (s,)}
            filter_db_query(context, TVShow.objects.all(), Movie.objects.all())
        except TypeError:
            pass



    def util_test_billing(self):
        user = self.get_user()
        user.billing.cc_num = ''
        user.billing.save()
        package_charge(user) #package charge with no cc num
        rental_charge(user) #rental charge with no cc num
        self.populate_billing(user) #add cc num
        user = self.create_subscription(user) #add sub
        package_charge(user) #charge with sub
        for x in range(10): #add 10 subs to trigger extra fee
            s = Subscription(siteuser=user, show=get_media('Bonanza'))
            s.save()
        package_charge(user) #charge with over basic plan # of slots
        for show in Subscription.objects.filter(siteuser=user, show=get_media('Bonanza')): #delete added subs
            show.delete()
        rental_charge(user) #rental charge with no rentals
        r = Rental(siteuser=user, movie=get_media('Frankenstein'), duration=20) #add rental
        r.save()
        rental_charge(user) #rental charge with unexpired rental
        r.delete()
        r = Rental(siteuser=user, movie=get_media('Frankenstein'), duration=-50) #add rental
        r.save()
        rental_charge(user) #rental charge with rental
        r.delete()


    def test_models(self):
        pass
        for name, model in apps.all_models['streaming'].items():
            print('Testing', name, 'to string')
            for item in model.objects.all():
                str(item)


    def test_decorators(self):
        client = Client()
        response = client.get('/streaming/login/') #get login page while logged out - no redirect
        self.assertEqual(response.status_code, 200)
        response = client.get('/streaming/') #get homepage while logged out - should redirect
        self.assertEqual(response.status_code, 302)

        client.login(username='test123', password='test')

        response = client.get('/streaming/login/') #get login page while logged in - should redirect
        self.assertEqual(response.status_code, 302)

        user = self.get_user()
        user.billing.next_payment_date = datetime.now() - timedelta(days=10)
        user.billing.save()
        self.generic_test('decorator @active_user', self.factory.get('/streaming/userpage/'), self.get_user(), user_page, 302) #test inactive account, should redirect

        temp_user = SiteUser.objects.get(username='test123')
        temp_user.last_login = datetime.now(timezone.utc) - timedelta(days=5)
        temp_user.save()
        client.get('/streaming/billing/') #get request should trigger relog



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
