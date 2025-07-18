from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView

from rooms.forms import CreateRoomForm, JoinRoomForm
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin

from rooms.models import Room


class CreateRoomView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'

    def get(self, request):
        form = CreateRoomForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        form = CreateRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            room.members.add(request.user)
            return redirect('room_detail', room.id)
        return render(request, 'form.html', {'form': form})

class RoomDetailView(LoginRequiredMixin,View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    def get(self, request, pk):
        room = Room.objects.get(pk=pk)
        if request.user != room.host and request.user not in room.members.all():
            raise PermissionDenied("You are not authorized to view this room.")
        return render(request,'room_detail.html', {'pk': pk})

class JoinRoomView(LoginRequiredMixin, View):
    login_url = '/accounts/login/'
    redirect_field_name = 'next'
    def get(self, request):
        form = JoinRoomForm()
        return render(request, 'form.html', {'form': form})


