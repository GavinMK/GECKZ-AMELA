from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'streaming'
urlpatterns = [
    path('createuser/', views.create_user_page, name='createUser'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_requested, name='logout'),
    path('', views.redirect_homepage, name='redirect_homepage'),
    path('home/', views.homepage, name='homepage'),
    path('userpage/', views.user_page, name='user_page'),
    path('friends/<str:username>', views.user_page, name='user_page'),
    path('movies/', views.movies, name='movies'),
    path('shows/', views.shows, name='shows'),
    path('account/', views.account_page, name='accountPage'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/messageInbox/', views.messageInbox, name='messageInbox'),
    path('inbox/sentInbox/', views.sentInbox, name='sentInbox'),
    path('inbox/readInbox/', views.readInbox, name='readInbox'),
    path('media/<str:title>/', views.display_media, name='display_media'),
    path('media/<str:title>/<int:season_number>/<int:episode_number>/', views.display_episode, name='display_episode'),
    path('search/', views.search, name="search"),
    path('comment/', views.post_comment, name="post_comment"),
    path('billing/', views.billing, name="billing"),
    path('change/', views.change, name="change"),
    path('friends/', views.friends, name="friends"),
    path('usersearch/', views.user_search, name="usersearch"),
    path('media/<str:title>/watch', views.watch_media, name='watch_media'),
    path('media/<str:title>/<int:season_number>/<int:episode_number>/watch', views.watch_media, name='watch_media'),
    path('media/<str:title>/<int:season_number>/<int:episode_number>/subscribe', views.subscription_page, name='subscribe'),
    path('media/<str:title>/unsubscribe', views.unsubscription_page, name='unsubscribe'),
    path('media/<str:title>/rent', views.rental_page, name='rental'),
    path('rate/', views.post_rating, name='post_rating'), # We should only need this until the javascript is working (I think)
    path('editProfile/', views.editProfile, name="editProfile"),
    path('about/', views.about, name="about"),
    path('inactiveAccount/', views.inactiveAccount, name='inactiveAccount'),
    path('cancelPlan/', views.cancel_plan, name='cancel_plan'),
    path('upload_picture/', views.profile_upload, name='upload_picture'),
    path('userpage/pick_photo/', views.pick_photo, name='pick_photo'),
]
