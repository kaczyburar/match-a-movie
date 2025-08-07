import pytest
from django.contrib.auth.models import User
from movies.models import Movie


@pytest.fixture
def user():

    return User.objects.create_user(username='test', password='test123')

@pytest.fixture
def movie():
    lst = []
    lst.append(Movie.objects.create(title='Test Movie'))
    lst.append(Movie.objects.create(title='Test Movie 2'))
    return lst