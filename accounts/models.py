from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = [
        ('TU', 'Tata Usaha'),
        ('PIM', 'Pimpinan'),
        ('SEKWAN', 'Sekwan'),
        ('KABAG', 'Kabag Umum'),
        ('KOMISI', 'Komisi'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    bidang_komisi = models.CharField(max_length=5, null=True, blank=True) # I, II, III, atau IV

    @property
    def role_status_matching(self):
        status_map = {
            'PIM': 'DI_PIMPINAN',
            'SEKWAN': 'DI_SEKWAN',
            'KABAG': 'DI_KABAG',
            'KOMISI': 'DI_KOMISI',
            'TU': ['REGISTRASI', 'DIJADWALKAN', 'VALIDASI_TU'],
        }
        return status_map.get(self.role, 'NONE')

    def __str__(self):
        return f"{self.user.username} - {self.role}"