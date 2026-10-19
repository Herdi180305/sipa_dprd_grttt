from .views import dashboard_overview, input_surat, daftar_surat, edit_surat, hapus_surat, detail_surat, cetak_tanda_terima, home, tracking_status, tentukan_jadwal, selesaikan_surat
from django.urls import path

urlpatterns = [
    path('', home, name='home'),
    path('status/<uuid:uuid>/', tracking_status, name='tracking_status'),
    path('dashboard/', dashboard_overview, name='dashboard'),
    path('input-surat/', input_surat, name='input_surat'),
    path('daftar-surat/', daftar_surat, name='daftar_surat'),
    path('edit-surat/<uuid:uuid>/', edit_surat, name='edit_surat'),
    path('hapus-surat/<uuid:uuid>/', hapus_surat, name='hapus_surat'),
    path('detail-surat/<uuid:uuid>/', detail_surat, name='detail_surat'),
    path('cetak-tanda-terima/<uuid:uuid>/', cetak_tanda_terima, name='cetak_tanda_terima'),
    path('surat/jadwal/<uuid:uuid>/', tentukan_jadwal, name='tentukan_jadwal'),
    path('surat/selesai/<uuid:uuid>/', selesaikan_surat, name='selesaikan_surat'),
]