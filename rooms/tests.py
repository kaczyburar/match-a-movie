
import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse
from rooms.models import Room


@pytest.mark.django_db
def test_room_menu_view_creates_room_successfully(user):
    client = Client()
    client.force_login(user[0])

    url = reverse('room_menu')
    data = {
        'name': 'test',
        'create_room': ''
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Room.objects.filter(name='test').exists()
    room = Room.objects.get(name='test')
    assert room.host.username == 'test'
    assert user[0] in room.members.all()

@pytest.mark.django_db
def test_room_menu_view_creation_room_unsuccessfully(room, user):
    client = Client()
    client.force_login(user[0])
    url = reverse('room_menu')
    data = {
        'name': 'Seans',
        'create_room': ''
    }
    response = client.post(url, data)
    form = response.context['create_room_form']

    assert response.status_code == 200
    assert 'name' in form.errors
    assert 'This name is already taken' in form.errors['name']

@pytest.mark.django_db
def test_user_can_access_room_detail_if_member_or_host(room, user):
    client = Client()
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_cant_access_room_detail_if_is_not_member_or_host(room, user):
    client = Client()
    client.force_login(user[1])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)
    assert response.status_code == 403

@pytest.mark.django_db
def test_room_menu_view_join_room_successfully_if_member_or_host(room, user):
    client = Client()
    client.force_login(user[0])
    url = reverse('room_menu')
    data = {
        'name': 'Seans',
        'join_room': ''
    }
    response = client.post(url, data)
    assert response.status_code == 302

@pytest.mark.django_db
def test_room_menu_view_join_room_unsuccessfully_room_not_exists(user):
    client = Client()
    client.force_login(user[0])
    url = reverse('room_menu')
    data = {
        'name': 'NonExistentRoom',
        'join_room': ''
    }
    response = client.post(url, data)
    form = response.context['join_room_form']

    assert response.status_code == 200
    assert 'name' in form.errors
    assert 'This room does not exist' in form.errors['name']