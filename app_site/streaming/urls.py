from django.urls import path, include

from . import views

app_name = 'streaming'
urlpatterns = [
    path('', views.index, name='index'),
    path('createuser/', views.create_user_page, name='createUser'),
    path('login/', views.login_page, name='login'),
    path('logout/', views.logout_requested, name='logout'),
    path('movie/<str:title>/', views.display_movie, name='display_movie'),
]
