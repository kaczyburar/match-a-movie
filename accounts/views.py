from django.shortcuts import render, redirect
from accounts.forms import RegisterUserForm
from django.views import View

class RegisterView(View):
    def get(self, request):
        form = RegisterUserForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('home')
        return render(request, 'form.html', {'form': form})