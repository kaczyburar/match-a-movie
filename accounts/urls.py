from django.urls import path
from accounts import views


urlpatterns = [
    path('register/', views.SignUpView.as_view(), name='signup'),
]