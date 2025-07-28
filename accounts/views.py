from urllib import request
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from accounts.forms import RegisterForm, LoginForm
from django.views import View


class HomeView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('login')
        else:
            return redirect('room_menu')
    def post(self, request):
        return redirect('register')


class RegisterView(View):
    def get(self, request):
        form = RegisterForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
        return render(request, 'form.html', {'form': form})

class LoginView(View):
    def get(self, request):
        form = LoginForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
        return render(request, 'nav_bar.html', {'form': form})

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')
