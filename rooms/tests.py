
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rooms.models import Room


@pytest.mark.django_db
def test_create_room_view_creates_room_successfully(user):
    client = Client()
    client.force_login(user[0])

    url = reverse('create_room')
    data = {
        'name': 'test'
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Room.objects.filter(name='test').exists()
    room = Room.objects.get(name='test')
    assert room.host.username == 'test'
    assert user[0] in room.members.all()

@pytest.mark.django_db
def test_create_room_view_creation_room_unsuccessfully(room, user):
    client = Client()
    client.force_login(user[0])
    url = reverse('create_room')
    data = {
        'name': 'Seans'
    }
    response = client.post(url, data)
    form = response.context['form']

    assert response.status_code == 200
    assert 'name' in form.errors
    assert 'This name is already taken' in form.errors['name']


