
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User



# Create your tests here.
@pytest.mark.django_db
def test_register_view():
    c = Client()
    url = reverse('register')
    response = c.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_register_password_and_confirm_password_match():
    c = Client()
    url = reverse('register')
    data = {
        'username': 'test',
        'password': 'polska123',
        'confirm_password': 'polska123',
    }
    response = c.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username='test').exists()

@pytest.mark.django_db
def test_register_password_and_confirm_password_mismatch():
    c = Client()
    url = reverse('register')
    data = {
        'username': 'test',
        'password': 'polska123',
        'confirm_password': 'koleszka123',
    }
    response = c.post(url, data)
    form = response.context['form']
    assert response.status_code == 200
    assert not User.objects.filter(username='test').exists()
    assert "Passwords don't match" in form.errors['confirm_password']




@pytest.mark.django_db
def test_register_user_already_exists(user):
    c = Client()
    url = reverse('register')
    data = {
        'username': 'test',
        'password': 'polska123',
        'confirm_password': 'polska123',
    }
    response = c.post(url, data)
    assert response.status_code == 200
    form = response.context['form']
    assert 'username' in form.errors
    assert 'A user with that username already exists.' in form.errors['username']

@pytest.mark.django_db
def test_register_password_too_short():
    c = Client()
    url = reverse('register')
    data = {
        'username': 'test',
        'password': '123',
        'confirm_password': '123',
    }
    response = c.post(url, data)
    assert response.status_code == 200
    form = response.context['form']
    assert 'password' in form.errors
    assert 'Password must be at least 8 characters' in form.errors['password']


