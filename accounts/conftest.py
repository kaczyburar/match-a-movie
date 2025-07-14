import pytest
from django.contrib.auth.models import User

@pytest.fixture
def user():
    lst = []
    lst.append(User.objects.create_user(username='test', password='polska123'))
    lst.append(User.objects.create_user(username='test2', password='djangomoc'))
    return lst