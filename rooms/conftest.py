import pytest
from django.contrib.auth.models import User

from rooms.models import Room


@pytest.fixture
def user():
    lst = []
    lst.append(User.objects.create_user(username='test', password='polska123'))
    lst.append(User.objects.create_user(username='test2', password='djangomoc'))
    return lst

@pytest.fixture
def room(user):
    room = Room.objects.create(name='Seans', host=user[0])
    room.members.add(user[0])
    return room



