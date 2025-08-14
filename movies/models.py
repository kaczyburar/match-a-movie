from django.contrib.auth.models import User
from django.db import models

from rooms.models import Room


class Movie(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    poster_url = models.URLField(max_length=500)
    trailer_url = models.URLField(max_length=500)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_ratings = models.IntegerField(default=0)

class MovieRating(models.Model):
    RATING_CHOICES = [
        ('0', 'dislike'),
        ('1', 'like'),
        ('2', 'love'),

    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='movie_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    rating = models.CharField(max_length=10, choices=RATING_CHOICES, null=True, blank=True)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'movie')

