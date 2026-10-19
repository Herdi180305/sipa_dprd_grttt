from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from surat.models import SuratAudiensi
from .models import Disposisi, Notifikasi
from django.contrib.auth.models import User
from .utils import kirim_email_disposisi  # Import helper email

@login_required
def proses_disposisi(request, uuid):
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    user_role = request.user.profile.role
    
    if request.method == 'POST':
        catatan_input = request.POST.get('catatan')
        
        if not catatan_input:
            messages.error(request, "Catatan tidak boleh kosong.")
            return redirect('detail_surat', uuid=surat.uuid)

        disposisi = Disposisi(
            surat=surat,
            pengirim=request.user,
            catatan=catatan_input,
            status_saat_itu=surat.status
        )
        
        # 1. Update status alur birokrasi
        if user_role == 'TU' and surat.status == 'REGISTRASI':
            surat.status = 'DI_PIMPINAN'
        elif user_role == 'PIM' and surat.status == 'DI_PIMPINAN':
            surat.status = 'DI_SEKWAN'
        elif user_role == 'SEKWAN' and surat.status == 'DI_SEKWAN':
            surat.status = 'DI_KABAG'
        elif user_role == 'KABAG' and surat.status == 'DI_KABAG':
            surat.status = 'VALIDASI_TU'
        elif user_role == 'TU' and surat.status == 'VALIDASI_TU':
            target_komisi = request.POST.get('tujuan_komisi')
            if target_komisi:
                surat.tujuan_komisi = target_komisi
                surat.status = 'DI_KOMISI'
                disposisi.catatan = f"[Ke Komisi {target_komisi}] - {catatan_input}"
            else:
                messages.error(request, "Pilih Komisi tujuan.")
                return redirect('detail_surat', uuid=surat.uuid)

        surat.save()
        disposisi.status_saat_itu = surat.status
        disposisi.save()

        # 2. Penentuan target penerima
        role_tujuan = None
        if surat.status == 'DI_PIMPINAN': role_tujuan = 'PIM'
        elif surat.status == 'DI_SEKWAN': role_tujuan = 'SEKWAN'
        elif surat.status == 'DI_KABAG': role_tujuan = 'KABAG'
        elif surat.status == 'VALIDASI_TU': role_tujuan = 'TU'
        elif surat.status == 'DI_KOMISI': role_tujuan = 'KOMISI'
        elif surat.status == 'DIJADWALKAN': role_tujuan = 'TU'

        if role_tujuan:
            penerima_users = User.objects.filter(profile__role=role_tujuan)
            if role_tujuan == 'KOMISI':
                penerima_users = penerima_users.filter(profile__bidang_komisi=surat.tujuan_komisi)

            # In-App Notification (Lonceng)
            for user_penerima in penerima_users:
                Notifikasi.objects.create(
                    penerima=user_penerima,
                    pesan=f"Surat {surat.kode_tracking} menunggu disposisi Anda.",
                    link=reverse('detail_surat', kwargs={'uuid': surat.uuid})
                )
            
            # TRIGGER EMAIL OTOMATIS
            kirim_email_disposisi(
                daftar_penerima_users=penerima_users,
                surat=surat,
                pengirim_user=request.user,
                catatan=disposisi.catatan
            )
        
        messages.success(request, f"Surat berhasil diteruskan ke: {surat.get_status_display()}")
            
    return redirect('detail_surat', uuid=surat.uuid)