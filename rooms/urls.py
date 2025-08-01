from django.urls import path
from rooms import views
from rooms.views import search_users

urlpatterns = [
    path('menu/', views.RoomView.as_view(), name='room_menu'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),

    path('<int:pk>/search/', search_users, name='search_users'),
    path('browse/', views.BrowseView.as_view(), name='browse'),




]