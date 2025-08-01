from django.contrib.auth.models import User
from django.db import models

from rooms.models import Room


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster_url = models.URLField(max_length=500)
    trailer_url = models.URLField(max_length=500)

class MovieRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='movie_ratings')
    rating = models.CharField(max_length=10)

    class Meta:
        unique_together = ('user', 'movie', 'room')

