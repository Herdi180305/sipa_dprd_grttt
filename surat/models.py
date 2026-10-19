import uuid
from django.db import models

class SuratAudiensi(models.Model):
    STATUS_CHOICES = [
        ('REGISTRASI', 'Registrasi di TU'),
        ('DI_PIMPINAN', 'Ditelaah Pimpinan'),
        ('KEMBALI_TU_1', 'Disposisi Kembali ke TU (dari PIM)'),
        ('DI_SEKWAN', 'Ditelaah Sekwan'),
        ('DI_KABAG', 'Ditelaah Kabag Umum'),
        ('DI_KOMISI', 'Koordinasi Jadwal Komisi'),
        ('DIJADWALKAN', 'Menunggu Surat Resmi (TU)'),
        ('SELESAI', 'Selesai / Surat Siap Diambil'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, primary_key=True)
    kode_tracking = models.CharField(max_length=20, unique=True)
    
    nama_pemohon = models.CharField(max_length=255)
    perihal = models.TextField()
    nomor_surat_pemohon = models.CharField(max_length=100, null=True, blank=True)
    tanggal_surat_pemohon = models.DateField(null=True, blank=True)
    
    tanggal_audiensi = models.DateTimeField(null=True, blank=True)
    waktu_audiensi = models.TimeField(null=True, blank=True)
    lokasi_audiensi = models.CharField(max_length=255, null=True, blank=True, default="Gedung DPRD Kabupaten Garut")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REGISTRASI')
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    request_tanggal = models.DateField(null=True, blank=True)
    tujuan_komisi = models.CharField(
        max_length=10, 
        choices=[('I', 'Komisi I'), ('II', 'Komisi II'), ('III', 'Komisi III'), ('IV', 'Komisi IV')],
        null=True, blank=True
    )

    objects = models.Manager()
    active_objects = models.Manager()
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.kode_tracking} - {self.nama_pemohon}"

    class Meta:
        verbose_name_plural = "Daftar Surat Audiensi"