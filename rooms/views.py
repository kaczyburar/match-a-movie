from pydoc import browse

from django.core.exceptions import PermissionDenied
from django.views import View
from rooms.forms import CreateRoomForm, JoinRoomForm
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from rooms.models import Room, JoinRequest
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
                room = Room.objects.get(name=room_name)
                if request.user != room.host and request.user not in room.members.all():
                    JoinRequest.objects.create(
                        room = room,
                        user=request.user
                    )
                else:
                    return redirect('room_detail', room.id)
            else:
                return render(request, 'room_menu.html', {
                    'create_room_form': CreateRoomForm(),
                    'join_room_form': form
                })

        return self.get(request)


class RoomDetailView(LoginRequiredMixin,View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    def get(self, request, pk):
        room = Room.objects.get(pk=pk)
        if request.user != room.host and request.user not in room.members.all():
            raise PermissionDenied("You are not authorized to view this room.")

        join_requests = []
        if request.user == room.host:
            join_requests = JoinRequest.objects.filter(room=room, status='pending')

        context = {
            'pk': pk,
            'room': room,
            'join_requests': join_requests
        }

        return render(request,'room_detail.html', context)

    def post(self, request, pk):
        room = Room.objects.get(pk=pk)

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

                if user_to_add not in room.members.all():
                    room.members.add(user_to_add)
                    messages.success(request, f'User {user_to_add.username} has been added to the room.')
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


class BrowseView(LoginRequiredMixin,View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    def get(self, request):
        user_rooms = Room.objects.filter(members=request.user)
        context = {
            'user_rooms': user_rooms
        }
        return render(request, 'room_browse.html', context)

