from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView

from rooms.forms import CreateRoomForm, JoinRoomForm
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages

from rooms.models import Room
from django.contrib.auth.models import User

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
                    raise PermissionDenied("You are not authorized to view this room.")
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

        all_users = User.objects.exclude(
            id=request.user.id
        ).exclude(
            id__in=room.members.all().values_list('id', flat=True)
        ).exclude(
            id=room.host.id
        ).values('id','username')


        users_list = list(all_users)



        context = {
            'pk': pk,
            'room': room,
            'users_data': users_list,
        }

        return render(request,'room_detail.html', context)

    def post(self, request, pk):
        room = Room.objects.get(pk=pk)

        username = request.POST.get('search_name')

        if username:
            try:
                user_to_add = User.objects.get(username=username)

                if user_to_add not in room.members.all():
                    room.members.add(user_to_add)
                    messages.success(request, f'Użytkownik {user_to_add.username} został dodany do pokoju.')
                else:
                    messages.warning(request, f'Użytkownik {user_to_add.username} już jest w pokoju.')

            except User.DoesNotExist:
                messages.error(request, f'Użytkownik {username} nie istnieje.')
        else:
            messages.error(request, 'Nie wybrano użytkownika.')

        return redirect('room_detail', pk=pk)




