from django.urls import path

from . import views

app_name = 'streaming'
urlpatterns = [
    path('', views.index, name='index'),
    path('createuser/', views.create_user_page, name='createUser'),
]