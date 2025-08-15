from pydoc import browse
from django.db.models import Count, Avg, Q
from django.core.exceptions import PermissionDenied
from django.views import View
from rooms.forms import CreateRoomForm, JoinRoomForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from rooms.models import Room, JoinRequest
from movies.models import Movie, MovieRating
from django.contrib.auth.models import User
from django.http import JsonResponse


class RoomView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request):
        create_room_form = CreateRoomForm()
        join_room_form = JoinRoomForm()
        return render(request, 'room_menu.html', {
            'create_room_form': create_room_form,
            'join_room_form': join_room_form
        })

    def post(self, request):
        if 'create_room' in request.POST:
            form = CreateRoomForm(request.POST)
            if form.is_valid():
                room = form.save(commit=False)
                room.host = request.user
                room.save()
                room.members.add(request.user)
                return redirect('room_detail', room.id)
            else:
                return render(request, 'room_menu.html', {
                    'create_room_form': form,
                    'join_room_form': JoinRoomForm()
                })

        elif 'join_room' in request.POST:
            form = JoinRoomForm(request.POST)
            if form.is_valid():
                room_name = form.cleaned_data['name']
                try:
                    room = Room.objects.get(name=room_name)
                    if request.user == room.host:
                        form.add_error('name', 'You are the host of this room')
                    elif request.user in room.members.all():
                        form.add_error('name', 'You are already a member of this room')
                    else:
                        existing_request = JoinRequest.objects.filter(room=room, user=request.user).first()
                        if existing_request:
                            form.add_error('name', 'Join request already sent')
                        else:
                            JoinRequest.objects.create(room=room, user=request.user)
                            form.add_error('name', 'Join request sent to host')
                except Room.DoesNotExist:
                    form.add_error('name', 'This room does not exist')

            return render(request, 'room_menu.html', {
                'create_room_form': CreateRoomForm(),
                'join_room_form': form
            })

        return self.get(request)


class RoomDetailView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request, pk):
        room = get_object_or_404(Room, pk=pk)
        if request.user != room.host and request.user not in room.members.all():
            raise PermissionDenied("You are not authorized to view this room.")

        join_requests = []
        if request.user == room.host:
            join_requests = JoinRequest.objects.filter(room=room, status='pending', request_type='request')

        room_members = room.members.all()

        movies_watched_by_all = Movie.objects.filter(
            ratings__user__in=room_members,
            ratings__watched=True
        ).annotate(
            watched_count=Count('ratings', filter=Q(ratings__watched=True, ratings__user__in=room_members))
        ).filter(
            watched_count=room_members.count()
        ).values_list('id', flat=True)

        top_movies = Movie.objects.filter(
            ratings__user__in=room_members
        ).exclude(
            id__in=movies_watched_by_all
        ).annotate(
            room_avg_rating=Avg('ratings__rating', filter=Q(ratings__user__in=room_members)),
            room_ratings_count=Count('ratings', filter=Q(ratings__user__in=room_members))
        ).filter(
            room_ratings_count__gt=0
        ).order_by(
            '-room_avg_rating',
            '-room_ratings_count'
        )[:10]

        movies_with_details = []
        for movie in top_movies:
            room_ratings = MovieRating.objects.filter(
                movie=movie,
                user__in=room_members
            )

            rating_breakdown = {
                'dislike': room_ratings.filter(rating='0').count(),
                'like': room_ratings.filter(rating='1').count(),
                'love': room_ratings.filter(rating='2').count(),
                'watched': room_ratings.filter(rating='3').count(),
            }

            movies_with_details.append({
                'movie': movie,
                'room_avg_rating': movie.room_avg_rating,
                'room_ratings_count': movie.room_ratings_count,
                'rating_breakdown': rating_breakdown,
            })

        context = {
            'pk': pk,
            'room': room,
            'join_requests': join_requests,
            'movies_with_details': movies_with_details,
            'room_members_count': room_members.count(),
        }

        return render(request, 'room_detail.html', context)

    def post(self, request, pk):
        room = Room.objects.get(pk=pk)

        if 'mark_watched_movie_id' in request.POST:
            if request.user != room.host:
                messages.error(request, 'Only the host can mark movies as watched for all members.')
                return redirect('room_detail', pk=pk)

            movie_id = request.POST.get('mark_watched_movie_id')
            try:
                movie = Movie.objects.get(id=movie_id)
                room_members = room.members.all()

                for member in room_members:
                    rating, created = MovieRating.objects.get_or_create(
                        user=member,
                        movie=movie,
                        defaults={'watched': True}
                    )
                    if not created:
                        rating.watched = True
                        rating.save()

                messages.success(request, f'Movie "{movie.title}" has been marked as watched for all room members.')
            except Movie.DoesNotExist:
                messages.error(request, 'Movie not found.')

            return redirect('room_detail', pk=pk)

        if 'join_request_id' in request.POST and 'action' in request.POST:
            join_request_id = request.POST.get('join_request_id')
            action = request.POST.get('action')

            try:
                join_request = JoinRequest.objects.get(id=join_request_id, room=room)
                if action == 'accept':
                    room.members.add(join_request.user)
                    join_request.delete()
                    messages.success(request, f'User {join_request.user.username} has been added to the room.')
                elif action == 'reject':
                    join_request.delete()
                    messages.info(request, f'User request rejected {join_request.user.username}')
            except JoinRequest.DoesNotExist:
                messages.error(request, 'Request does not exist.')

            return redirect('room_detail', pk=pk)

        username = request.POST.get('search_name')
        if username:
            try:
                user_to_add = User.objects.get(username=username)
                has_pending_request = JoinRequest.objects.filter(room=room, user=user_to_add).exists()

                if user_to_add not in room.members.all() and not has_pending_request:
                    JoinRequest.objects.create(
                        room=room,
                        user=user_to_add,
                        request_type='invitation'
                    )
                    messages.success(request, 'Invitation has been sent.')
                else:
                    messages.warning(request, f'User {user_to_add.username} is already in the room.')

            except User.DoesNotExist:
                messages.error(request, f'User {username} does not exist.')
        else:
            messages.error(request, 'No user selected.')

        return redirect('room_detail', pk=pk)


def search_users(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        room = Room.objects.get(pk=pk)
        if request.user != room.host and request.user not in room.members.all():
            return JsonResponse({'error': 'Access denied'}, status=403)
    except Room.DoesNotExist:
        return JsonResponse({'error': 'Room not found'}, status=404)

    query = request.GET.get('q', '').strip()

    if len(query) < 3:
        return JsonResponse({'users': []})

    users = User.objects.exclude(
        id__in=room.members.all().values_list('id', flat=True)
    ).filter(
        username__icontains=query
    ).values('id', 'username')[:10]

    return JsonResponse({'users': list(users)})


class BrowseView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request):
        user_rooms = Room.objects.filter(members=request.user)

        join_requests = JoinRequest.objects.filter(
            user_id=request.user,
            status='pending',
            request_type='invitation'
        )

        sent_requests = JoinRequest.objects.filter(
            user_id=request.user,
            status='pending',
            request_type='request'
        )

        context = {
            'user_rooms': user_rooms,
            'join_requests': join_requests,
            'sent_requests': sent_requests,
        }
        return render(request, 'room_browse.html', context)

    def post(self, request):
        if 'join_request_id' in request.POST and 'action' in request.POST:
            join_request_id = request.POST.get('join_request_id')
            room_id = request.POST.get('room_id')
            action = request.POST.get('action')

            try:
                join_request = JoinRequest.objects.get(id=join_request_id, room=room_id)
                room = Room.objects.get(pk=room_id)

                if action == 'accept':
                    room.members.add(join_request.user)
                    join_request.delete()
                    messages.success(request, f'You have joined the room {room.name}.')
                elif action == 'reject':
                    join_request.delete()
                    messages.info(request, f'You have rejected the invitation to {room.name}.')
                elif action == 'cancel':
                    join_request.delete()
                    messages.info(request, f'You have cancelled your request to join {room.name}.')

            except JoinRequest.DoesNotExist:
                messages.error(request, 'Request does not exist.')
            except Room.DoesNotExist:
                messages.error(request, 'Room does not exist.')

        return redirect('browse')