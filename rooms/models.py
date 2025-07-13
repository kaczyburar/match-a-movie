from django.contrib.auth.models import User
from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=50)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_room')
    members = models.ManyToManyField(User, related_name='joined_room')

