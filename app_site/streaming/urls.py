from django.urls import path, include

from . import views

app_name = 'streaming'
urlpatterns = [
    path('datadump/', views.index, name='index'),
    path('createuser/', views.create_user_page, name='createUser'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_requested, name='logout'),
    path('', views.homepage, name='homepage'),
    path('account/', views.user_page, name='user_page'),
    path('movies/', views.movies, name='movies'),
    path('shows/', views.shows, name='shows'),
    path('account/', views.account_page, name='accountPage'),
    path('media/<str:title>/', views.display_media, name='display_media'),
    path('media/<str:title>/<int:season_number>/<int:episode_number>/', views.display_episode, name='display_episode'),
    path('search/', views.search, name="search"),
]
