from django.shortcuts import render
from django.views import View
from rooms.forms import CreateRoomForm
from django.shortcuts import render, redirect


class CreateRoomView(View):
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

