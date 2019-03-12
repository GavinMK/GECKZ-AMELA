from django.urls import path, include

from . import views

app_name = 'streaming'
urlpatterns = [
    path('', views.index, name='index'),
    path('createuser/', views.create_user_page, name='createUser'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_requested, name='logout'),
    path('homepage/', views.homepage, name='homepage'),
    path('media/<str:title>/', views.display_media, name='display_media'),
    path('media/<str:title>/<int:season_number>/<int:episode_number>/', views.display_episode, name='display_episode'),
]
