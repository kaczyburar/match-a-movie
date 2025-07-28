from django import forms

from rooms.models import Room


class CreateRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())

    def clean(self):
        data = super().clean()
        name = data.get('name')
        if name and Room.objects.filter(name__iexact=data['name']).exists():
            self.add_error("name", "This name is already taken")

        return data

    class Meta:
        model = Room
        fields = ['name']

class JoinRoomForm(forms.ModelForm):
    name = forms.CharField(widget=forms.TextInput())

    def clean(self):
        data = super().clean()
        name = data.get('name')

        if name and not Room.objects.filter(name__iexact=data['name']).exists():
            self.add_error("name", "This room does not exist")
        return data

    class Meta:
        model = Room
        fields = ['name']