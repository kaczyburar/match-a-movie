from http.client import responses

import pytest
from _pytest import pytester
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.exceptions import PermissionDenied
from django.test import Client
from django.urls import reverse
from rooms.models import Room, JoinRequest
from movies.models import Movie, MovieRating


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

@pytest.mark.django_db
def test_room_detail_get_as_host(client, user, room):
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert f'{user[0].username} (Host)' in response.content.decode()

@pytest.mark.django_db
def test_room_detail_get_as_member(client, user, room):
    room.members.add(user[1])
    client.force_login(user[1])
    url = reverse('room_detail', kwargs={'pk': room.pk})

    response = client.get(url)
    assert response.status_code == 200
    assert user[1].username in response.content.decode()

@pytest.mark.django_db
def test_room_detail_get_unauthorized_user(client, room):
    unauthorized_user = User.objects.create_user(username='unauthorized', password='test12345')
    client.force_login(unauthorized_user)
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 403

@pytest.mark.django_db
def test_room_detail_get_anonymous_user(client, room):
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert '/accounts/login/' in response.url

@pytest.mark.django_db
def test_invite_user_to_room_success(client, user, room):
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    assert not room.members.filter(username=user[1].username).exists()

    response = client.post(url, {'search_name': user[1].username})

    assert response.status_code == 302
    room.refresh_from_db()
    assert JoinRequest.objects.filter(room=room, user=user[1],request_type='invitation' ).exists()
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert 'Invitation has been sent.' in str(messages[0])

@pytest.mark.django_db
def test_invite_join_request_accepted(client, user, room):

    join_request = JoinRequest.objects.create(room=room, user=user[1], request_type='invitation')
    client.force_login(user[0])
    url = reverse('browse')
    assert not room.members.filter(username=user[1].username).exists()

    response = client.post(url, {
        'join_request_id': join_request.id,
        'room_id': room.pk,
        'action': 'accept'
    })
    assert response.status_code == 302
    room.refresh_from_db()
    assert room.members.filter(username=user[1].username).exists()
    assert not JoinRequest.objects.filter(room=room, user=user[1]).exists()
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert f'User {user[1].username} has been added to the room.' in str(messages[0])

@pytest.mark.django_db
def test_invite_join_request_rejected(client, user, room):

    join_request = JoinRequest.objects.create(room=room, user=user[1], request_type='invitation')
    client.force_login(user[0])
    url = reverse('browse')
    assert not room.members.filter(username=user[1].username).exists()

    response = client.post(url, {
        'join_request_id': join_request.id,
        'room_id': room.pk,
        'action': 'reject'
    })
    assert response.status_code == 302
    room.refresh_from_db()
    assert not room.members.filter(username=user[1].username).exists()
    assert not JoinRequest.objects.filter(room=room, user=user[1]).exists()




@pytest.mark.django_db
def test_add_existing_member_warning(client, user, room):
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.post(url, {'search_name': user[0].username})

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert f'User {user[0].username} is already in the room.' in str(messages[0])

@pytest.mark.django_db
def test_add_nonexistent_user_error(client, user, room):
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.post(url, {'search_name': 'nonexistent_usr'})

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert f'User nonexistent_usr does not exist.' in str(messages[0])

@pytest.mark.django_db
def test_user_creates_join_request_when_not_member(client, user, room):
    client.force_login(user[1])
    url = reverse('room_menu')
    data = {
        'name': 'Seans',
        'join_room': ''
    }
    response = client.post(url, data)
    assert JoinRequest.objects.filter(room=room, user=user[1]).exists()
    join_reqeust = JoinRequest.objects.get(room=room, user=user[1])
    assert join_reqeust.status == 'pending'

@pytest.mark.django_db
def test_host_can_see_join_reqeust_in_room_detail(client, user, room):
    JoinRequest.objects.create(room=room, user=user[1])
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert 'join_requests' in response.context
    assert len(response.context['join_requests']) == 1
    assert user[1].username in response.content.decode()

@pytest.mark.django_db
def test_member_cannot_see_join_reqeust(client, user, room):
    room.members.add(user[1])
    JoinRequest.objects.create(room=room, user=user[2])
    client.force_login(user[1])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['join_requests']) == 0

@pytest.mark.django_db
def test_accept_join_reqeust_success(client, user, room):
    join_request = JoinRequest.objects.create(room=room, user=user[1])
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})

    assert not room.members.filter(username=user[1]).exists()

    response = client.post(url, {
        'join_request_id': join_request.id,
        'action': 'accept'
    })

    assert response.status_code == 302
    room.refresh_from_db()
    assert room.members.filter(username=user[1].username).exists()
    assert not JoinRequest.objects.filter(room=room, user=user[1]).exists()

    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert f'User {user[1].username} has been added to the room.' in str(messages[0])

@pytest.mark.django_db
def test_reject_join_reqeust_success(client, user, room):
    join_request = JoinRequest.objects.create(room=room, user=user[1])
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})

    assert not room.members.filter(username=user[1]).exists()

    response = client.post(url, {
        'join_request_id': join_request.id,
        'action': 'reject'
    })
    assert response.status_code == 302
    room.refresh_from_db()

    assert not room.members.filter(username=user[1].username).exists()
    assert not JoinRequest.objects.filter(room=room, user=user[1]).exists()

@pytest.mark.django_db
def test_duplicate_join_request_prevention(client, user, room):
    JoinRequest.objects.create(room=room, user=user[1])
    client.force_login(user[1])
    url = reverse('room_menu')
    data = {
        'name': 'Seans',
        'join_room': ''
    }
    with pytest.raises(Exception):
        client.post(url, data)


@pytest.mark.django_db
def test_room_detail_shows_top_movies_for_room_members(client, user, room, movies):
    room.members.add(user[1])

    MovieRating.objects.create(user=user[0], movie=movies[0], rating='2')
    MovieRating.objects.create(user=user[1], movie=movies[0], rating='2')
    MovieRating.objects.create(user=user[0], movie=movies[1], rating='1')

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert 'movies_with_details' in response.context
    assert len(response.context['movies_with_details']) == 2

    first_movie = response.context['movies_with_details'][0]
    assert first_movie['movie'].title == 'Great Movie'
    assert first_movie['room_avg_rating'] == 2.0
    assert first_movie['room_ratings_count'] == 2


@pytest.mark.django_db
def test_room_detail_shows_no_movies_when_no_ratings(client, user, room, movies):
    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert 'movies_with_details' in response.context
    assert len(response.context['movies_with_details']) == 0


@pytest.mark.django_db
def test_room_detail_excludes_ratings_from_non_members(client, user, room, movies):
    non_member = User.objects.create_user(username='outsider', password='test12345')

    MovieRating.objects.create(user=user[0], movie=movies[0], rating='1')
    MovieRating.objects.create(user=non_member, movie=movies[0], rating='2')

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    movies_with_details = response.context['movies_with_details']
    assert len(movies_with_details) == 1

    movie_data = movies_with_details[0]
    assert movie_data['room_avg_rating'] == 1.0
    assert movie_data['room_ratings_count'] == 1


@pytest.mark.django_db
def test_room_detail_limits_to_10_movies_max(client, user, room):
    for i in range(15):
        movie = Movie.objects.create(
            title=f'Movie {i}',
            description=f'Description {i}',
            poster_url=f'http://example.com/poster{i}.jpg',
            trailer_url=f'http://example.com/trailer{i}.mp4'
        )
        MovieRating.objects.create(user=user[0], movie=movie, rating='1')

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert len(response.context['movies_with_details']) == 10


@pytest.mark.django_db
def test_room_detail_sorts_movies_by_average_rating(client, user, room, movies):
    room.members.add(user[1])

    MovieRating.objects.create(user=user[0], movie=movies[2], rating='0')
    MovieRating.objects.create(user=user[1], movie=movies[2], rating='1')

    MovieRating.objects.create(user=user[0], movie=movies[0], rating='2')
    MovieRating.objects.create(user=user[1], movie=movies[0], rating='2')

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    movies_with_details = response.context['movies_with_details']
    assert len(movies_with_details) == 2

    assert movies_with_details[0]['movie'].title == 'Great Movie'
    assert movies_with_details[0]['room_avg_rating'] == 2.0

    assert movies_with_details[1]['movie'].title == 'Average Movie'
    assert movies_with_details[1]['room_avg_rating'] == 0.5


@pytest.mark.django_db
def test_room_detail_rating_breakdown_accuracy(client, user, room, movies):
    room.members.add(user[1])
    room.members.add(user[2])

    MovieRating.objects.create(user=user[0], movie=movies[0], rating='0')
    MovieRating.objects.create(user=user[1], movie=movies[0], rating='1')
    MovieRating.objects.create(user=user[2], movie=movies[0], rating='2')

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    movie_data = response.context['movies_with_details'][0]
    rating_breakdown = movie_data['rating_breakdown']

    assert rating_breakdown['dislike'] == 1
    assert rating_breakdown['like'] == 1
    assert rating_breakdown['love'] == 1
    assert rating_breakdown['watched'] == 0


@pytest.mark.django_db
def test_room_detail_includes_room_members_count(client, user, room):
    room.members.add(user[1])
    room.members.add(user[2])

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert 'room_members_count' in response.context
    assert response.context['room_members_count'] == 3


@pytest.mark.django_db
def test_room_detail_movies_context_exists_for_non_host(client, user, room, movies):
    room.members.add(user[1])

    MovieRating.objects.create(user=user[0], movie=movies[0], rating='1')

    client.force_login(user[1])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    assert response.status_code == 200
    assert 'movies_with_details' in response.context
    assert 'room_members_count' in response.context
    assert len(response.context['movies_with_details']) == 1


@pytest.mark.django_db
def test_room_detail_movies_with_same_rating_sorted_by_count(client, user, room, movies):
    room.members.add(user[1])
    room.members.add(user[2])

    MovieRating.objects.create(user=user[0], movie=movies[0], rating='2')

    MovieRating.objects.create(user=user[1], movie=movies[1], rating='2')
    MovieRating.objects.create(user=user[2], movie=movies[1], rating='2')

    client.force_login(user[0])
    url = reverse('room_detail', kwargs={'pk': room.pk})
    response = client.get(url)

    movies_with_details = response.context['movies_with_details']
    assert len(movies_with_details) == 2

    assert movies_with_details[0]['movie'].title == 'Good Movie'
    assert movies_with_details[0]['room_ratings_count'] == 2

    assert movies_with_details[1]['movie'].title == 'Great Movie'
    assert movies_with_details[1]['room_ratings_count'] == 1

