from django import forms
from .models import Disposisi

class DisposisiForm(forms.ModelForm):
    class Meta:
        model = Disposisi
        fields = ['catatan']
        widgets = {
            'catatan': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3, 
                'placeholder': 'Tuliskan instruksi atau catatan disposisi di sini...'
            }),
        }