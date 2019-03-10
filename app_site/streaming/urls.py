from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('createuser/', views.create_user, name='createUser'),
]