from django.shortcuts import render
from django.views import View
from rooms.forms import CreateRoomForm



    # def post(self, request):
    #     form = RegisterForm(request.POST)
    #     if form.is_valid():
    #         user = form.save(commit=False)
    #         user.set_password(form.cleaned_data['password'])
    #         user.save()
    #         return redirect('home')
    #     return render(request, 'form.html', {'form': form})
    #
class CreateRoomView(View):
    def get(self, request):
        form = CreateRoomForm()
        return render(request, 'form.html', {'form': form})