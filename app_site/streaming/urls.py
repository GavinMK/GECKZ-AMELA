from django.urls import path, include
from django.conf.urls import url

from . import views

app_name = 'streaming'
urlpatterns = [
    path('createuser/', views.create_user_page, name='createUser'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_requested, name='logout'),
    path('', views.homepage, name='homepage'),
    path('userpage/', views.user_page, name='user_page'),
    path('userpage/<str:username>', views.user_page, name='user_page'),
    path('movies/', views.movies, name='movies'),
    path('shows/', views.shows, name='shows'),
    path('account/', views.account_page, name='accountPage'),
    path('inbox/', views.inbox, name='inbox'),
    path('messageInbox/', views.messageInbox, name='messageInbox'),
    path('sentInbox/', views.sentInbox, name='sentInbox'),
    path('readInbox/', views.readInbox, name='readInbox'),
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
    path('media/<str:title>/rent', views.rental_page, name='rental'),
    path('rate/', views.post_rating, name='post_rating'), # We should only need this until the javascript is working (I think)
    path('editProfile/', views.editProfile, name="editProfile"),
    path('inactiveAccount/', views.inactiveAccount, name='inactiveAccount'),
    path('cancelPlan/', views.cancel_plan, name='cancel_plan'),
]
