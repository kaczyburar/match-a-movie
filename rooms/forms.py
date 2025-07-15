from django import forms

from rooms.models import Room


class CreateRoomForm(forms.ModelForm):
    room_name = forms.CharField(widget=forms.TextInput())

    class Meta:
        model = Room
        fields = ['room_name']