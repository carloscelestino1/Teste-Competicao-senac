from django import forms
from .models import *

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            'title',
            'max_capacity',
            'description',
            'date',
            'start_at',
            'status',
            'User_cpf',
            'image'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Título do evento'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'input-field', 'placeholder': 'Capacidade máxima'}),
            'description': forms.Textarea(attrs={'class': 'input-field', 'rows': 5}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'input-field'}),
            'start_at': forms.TimeInput(attrs={'type': 'time', 'class': 'input-field'}),
            'status': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Status do evento'}),
            'User_cpf': forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'CPF do responsável'}),
            'image': forms.ClearableFileInput(attrs={'class': 'input-field'}),
        }


class EventAdressForm(forms.ModelForm):
    class Meta:
        model = EventAdress
        exclude = ['event']
        widgets = {
            'uf': forms.TextInput(attrs={'class': 'input-field'}),
            'city': forms.TextInput(attrs={'class': 'input-field'}),
            'neighborhood': forms.TextInput(attrs={'class': 'input-field'}),
            'street': forms.TextInput(attrs={'class': 'input-field'}),
            'number': forms.TextInput(attrs={'class': 'input-field'}),
            'complement': forms.TextInput(attrs={'class': 'input-field'}),
            'cep': forms.TextInput(attrs={'class': 'input-field'}),
        }