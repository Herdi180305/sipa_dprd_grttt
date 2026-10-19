from django import forms
from .models import SuratAudiensi

class SuratMasukForm(forms.ModelForm):
    class Meta:
        model = SuratAudiensi
        fields = ['nama_pemohon', 'nomor_surat_pemohon', 'tanggal_surat_pemohon', 'perihal', 'request_tanggal']
        widgets = {
            'nama_pemohon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama Instansi/Individu'}),
            'nomor_surat_pemohon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contoh: 123/ST/V/2026'}),
            'tanggal_surat_pemohon': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'perihal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ringkasan isi surat'}),
            'request_tanggal': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }