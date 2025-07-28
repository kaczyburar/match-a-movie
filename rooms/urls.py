from django.urls import path
from rooms import views

urlpatterns = [
    path('menu/', views.RoomView.as_view(), name='room_menu'),
    path('<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),


]