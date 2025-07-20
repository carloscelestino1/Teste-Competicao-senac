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

class SectorForm(forms.ModelForm):
    class Meta:
        model = Sector
        fields = ['title', 'max_capacity', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input-field'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'input-field'}),
            'status': forms.Select(attrs={'class': 'input-field'}),
        }

    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        max_capacity = cleaned_data.get('max_capacity')
        if self.instance.pk:
            setores = Sector.objects.filter(Event_id=self.instance.Event_id).exclude(pk=self.instance.pk)
        else:
            setores = Sector.objects.filter(Event_id=self.event)

        soma = sum(s.max_capacity for s in setores)
        if self.event and max_capacity and soma + max_capacity > self.event.max_capacity:
            self.add_error('max_capacity', 'Capacidade total dos setores excede a capacidade máxima do evento.')
