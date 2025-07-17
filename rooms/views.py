from django.shortcuts import render
from django.views import View
from rooms.forms import CreateRoomForm
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin


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
            return redirect('home')
        return render(request, 'form.html', {'form': form})

