import pytest
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client
from django.urls import reverse
from movies.models import Movie, MovieRating

@pytest.mark.django_db
def test_movie_rating_view_get_anonymous_user():
    client = Client()
    url = reverse('rate_movie')
    response = client.get(url)

    assert response.status_code == 302
    assert '/accounts/login/' in response.url

@pytest.mark.django_db
def test_movie_rating_view_get_authenticated_user_with_movies(user, movie):
    client = Client()
    client.force_login(user)
    url = reverse('rate_movie')

    response = client.get(url)

    assert response.status_code == 200
    assert 'movie' in response.context
    assert 'rating_choices' in response.context
    assert response.context['movie'] == movie[0]
    assert 'all_rated' not in response.context

@pytest.mark.django_db
def test_movie_rating_view_get_all_movies_rated(user, movie):
    client = Client()
    client.force_login(user)
    MovieRating.objects.create(user=user, movie=movie[0], rating='3')
    MovieRating.objects.create(user=user, movie=movie[1], rating='2')

    url = reverse('rate_movie')
    response = client.get(url)
    assert response.status_code == 200
    assert response.context['all_rated'] is True
    assert 'movie' not in response.context

@pytest.mark.django_db
def test_movie_rating_view_youtube_embed_url_watch_format(user):
    client = Client()
    client.force_login(user)

    movie = Movie.objects.create(
        title = 'Test Movie',
        trailer_url = 'https://www.youtube.com/watch?v=id1P7M6l2eQ'
    )

    url = reverse('rate_movie')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['youtube_embed_url'] == 'https://www.youtube.com/embed/id1P7M6l2eQ'

@pytest.mark.django_db
def test_movie_rating_view_youtube_embed_youtu_be_format(user):
    client = Client()
    client.force_login(user)

    movie = Movie.objects.create(
        title='Test Movie',
        trailer_url='https://youtu.be/dQw4w9WgXcQ?t=10'
    )

    url = reverse('rate_movie')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['youtube_embed_url'] == 'https://www.youtube.com/embed/dQw4w9WgXcQ'

@pytest.mark.django_db
def test_movie_rating_view_no_trailer_url(user):
    client = Client()
    client.force_login(user)

    movie = Movie.objects.create(title='Test Movie')

    url = reverse('rate_movie')
    response = client.get(url)
    assert response.status_code == 200
    assert 'youtube_embed_url' not in response.context


@pytest.mark.django_db
def test_movie_rating_post_successful_rating(user, movie):
    client = Client()
    client.force_login(user)
    url = reverse('rate_movie')

    response = client.post(url, {'rating': '3'})

    assert response.status_code == 302
    assert MovieRating.objects.filter(user=user, movie=movie[0], rating='3').exists()

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert f'You rated: {movie[0].title}' in str(messages[0])


@pytest.mark.django_db
def test_movie_rating_post_updates_movie_stats(user, movie):
    client = Client()
    client.force_login(user)
    url = reverse('rate_movie')

    other_user = User.objects.create_user(username='other', password='test123')
    MovieRating.objects.create(user=other_user, movie=movie[0], rating='1')

    client.post(url, {'rating': '3'})

    movie[0].refresh_from_db()
    assert movie[0].average_rating == 2.0  # (1 + 3) / 2
    assert movie[0].total_ratings == 2


@pytest.mark.django_db
def test_movie_rating_post_all_movies_rated(user, movie):
    client = Client()
    client.force_login(user)
    MovieRating.objects.create(user=user, movie=movie[0], rating='2')
    MovieRating.objects.create(user=user, movie=movie[1], rating='3')

    url = reverse('rate_movie')
    response = client.post(url, {'rating': '3'})

    assert response.status_code == 302
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert 'No movies to rate.' in str(messages[0])


@pytest.mark.django_db
def test_movie_rating_excludes_already_rated_movies(user, movie):
    client = Client()
    client.force_login(user)

    MovieRating.objects.create(user=user, movie=movie[0], rating='3')

    url = reverse('rate_movie')
    response = client.get(url)

    assert response.status_code == 200
    assert response.context['movie'] == movie[1]