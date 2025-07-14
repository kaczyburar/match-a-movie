
import pytest
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User



# Create your tests here.
@pytest.mark.django_db
def test_signup_view():
    c = Client()
    url = reverse('signup')
    response = c.get(url)
    assert response.status_code == 200

@pytest.mark.django_db
def test_signup_password_and_confirm_password_match():
    c = Client()
    url = reverse('signup')
    data = {
        'username': 'test',
        'password': 'polska123',
        'confirm_password': 'polska123',
    }
    response = c.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username='test').exists()

@pytest.mark.django_db
def test_signup_password_and_confirm_password_mismatch():
    c = Client()
    url = reverse('signup')
    data = {
        'username': 'test',
        'password': 'polska123',
        'confirm_password': 'koleszka123',
    }
    response = c.post(url, data)
    assert response.status_code == 200
    assert not User.objects.filter(username='test').exists()
