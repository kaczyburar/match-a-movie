from django import forms

from rooms.models import Room


class CreateRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())

    def clean(self):
        data = super().clean()
        if Room.objects.filter(name__iexact=data['name']).exists():
            self.add_error("name", "This name is already taken")

    class Meta:
        model = Room
        fields = ['name']

class JoinRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())

    def clean(self):
        data = super().clean()
        if not Room.objects.filter(name__iexact=data['name']).exists():
            self.add_error("name", "This room does not exist")

    class Meta:
        model = Room
        fields = ['name']