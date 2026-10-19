from django.db import models
from django.contrib.auth.models import User
from surat.models import SuratAudiensi

class Disposisi(models.Model):
    surat = models.ForeignKey(SuratAudiensi, on_delete=models.CASCADE, related_name='riwayat_disposisi')
    
    pengirim = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disposisi_keluar')
    penerima = models.ForeignKey(User, on_delete=models.CASCADE, related_name='disposisi_masuk', null=True, blank=True)
    
    catatan = models.TextField()
    
    status_saat_itu = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Disposisi {self.surat.kode_tracking} dari {self.pengirim.username}"

class Notifikasi(models.Model):
    penerima = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifikasi')
    pesan = models.CharField(max_length=255)
    link = models.CharField(max_length=255, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notif untuk {self.penerima.username}: {self.pesan}"