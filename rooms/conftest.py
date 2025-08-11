import pytest
from django.contrib.auth.models import User

from rooms.models import Room
from movies.models import Movie

@pytest.fixture
def user():
    lst = []
    lst.append(User.objects.create_user(username='test', password='polska123'))
    lst.append(User.objects.create_user(username='test2', password='djangomoc'))
    lst.append(User.objects.create_user(username='test3', password='kokoszek'))
    return lst

@pytest.fixture
def room(user):
    room = Room.objects.create(name='Seans', host=user[0])
    room.members.add(user[0])
    return room

@pytest.fixture
def movies():
    lst = []
    lst.append(Movie.objects.create(
        title='Great Movie',
        description='Amazing film',
        poster_url='http://example.com/poster1.jpg',
        trailer_url='http://example.com/trailer1.mp4'
    ))
    lst.append(Movie.objects.create(
        title='Good Movie',
        description='Nice film',
        poster_url='http://example.com/poster2.jpg',
        trailer_url='http://example.com/trailer2.mp4'
    ))
    lst.append(Movie.objects.create(
        title='Average Movie',
        description='Mediocre film',
        poster_url='http://example.com/poster3.jpg',
        trailer_url='http://example.com/trailer3.mp4'
    ))
    return lst


