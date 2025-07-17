from django.urls import path
from rooms import views

urlpatterns = [
    path('create_room/', views.CreateRoomView.as_view(), name='create_room'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room_detail'),
]