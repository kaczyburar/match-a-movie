from django.contrib.auth.models import User
from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=50)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_room')
    members = models.ManyToManyField(User, related_name='joined_room')

class JoinRequest(models.Model):
    REQUEST_TYPE_CHOICES = [
        ('invitation', 'Invitation'),
        ('request', 'Request'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='join_request')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_request')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_type = models.CharField(max_length=10, choices=REQUEST_TYPE_CHOICES, default='request')


    class Meta:
        unique_together = ('room', 'user')