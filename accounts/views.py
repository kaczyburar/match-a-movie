from django.shortcuts import render, redirect
from accounts.forms import SignUpForm
from django.views import View

class SignUpView(View):
    def get(self, request):
        form = SignUpForm()
        return render(request, 'form.html', {'form': form})

    def post(self, request):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('home')
        return render(request, 'form.html', {'form': form})