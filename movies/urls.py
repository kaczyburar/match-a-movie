# movies/urls.py
from django.urls import path
from . import views



urlpatterns = [
    path('detail/', views.MovieRatingView.as_view(), name='rate_movie'),

    path('detail/<int:movie_id>/', views.MovieRatingView.as_view(), name='rate_movie_specific'),
]