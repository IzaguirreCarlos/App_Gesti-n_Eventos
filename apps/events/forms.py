from django import forms
from .models import Event, Category
from django.utils import timezone


class EventForm(forms.ModelForm):
    start_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'short_description', 'category', 'event_type',
            'start_date', 'end_date', 'location', 'address', 'virtual_link',
            'virtual_platform', 'max_capacity', 'cover_image', 'is_public',
            'is_free', 'price', 'tags', 'status',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Título del evento'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 5}),
            'short_description': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'category': forms.Select(attrs={'class': 'form-input'}),
            'event_type': forms.Select(attrs={'class': 'form-input'}),
            'location': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ciudad, País'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2}),
            'virtual_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://zoom.us/...'}),
            'virtual_platform': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Zoom, Meet, Teams...'}),
            'max_capacity': forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
            'price': forms.NumberInput(attrs={'class': 'form-input', 'step': '0.01', 'min': '0'}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'tecnología, música, arte'}),
            'status': forms.Select(attrs={'class': 'form-input'}),
            'is_public': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_free': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start = cleaned_data.get('start_date')
        end = cleaned_data.get('end_date')
        if start and end:
            if end <= start:
                raise forms.ValidationError('La fecha de fin debe ser posterior a la de inicio.')
            if start < timezone.now() and not self.instance.pk:
                raise forms.ValidationError('La fecha de inicio no puede ser en el pasado.')
        return cleaned_data


class EventFilterForm(forms.Form):
    q = forms.CharField(required=False, widget=forms.TextInput(attrs={'placeholder': 'Buscar eventos...', 'class': 'form-input'}))
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, empty_label='Todas las categorías', widget=forms.Select(attrs={'class': 'form-input'}))
    event_type = forms.ChoiceField(choices=[('', 'Todos'), ('presential', 'Presencial'), ('virtual', 'Virtual'), ('hybrid', 'Híbrido')], required=False, widget=forms.Select(attrs={'class': 'form-input'}))
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-input'}))
