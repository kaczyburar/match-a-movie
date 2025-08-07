# movies/urls.py
from django.urls import path
from . import views



urlpatterns = [
    # URL do oceniania filmów - pierwszy nieoceniony film
    path('detail/', views.MovieRatingView.as_view(), name='rate_movie'),

    # URL do oceniania konkretnego filmu
    path('detail/<int:movie_id>/', views.MovieRatingView.as_view(), name='rate_movie_specific'),
]