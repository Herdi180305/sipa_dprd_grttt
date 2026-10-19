from django.core.mail import send_mail
from django.conf import settings

def kirim_email_disposisi(daftar_penerima_users, surat, pengirim_user, catatan):
    """
    Mengirimkan notifikasi email ke daftar user penerima disposisi.
    """
    # Filter hanya user yang memiliki alamat email terdaftar
    email_tujuan = [u.email for u in daftar_penerima_users if u.email]
    
    if not email_tujuan:
        return

    subject = f"[E-AUDIENSI DPRD] Disposisi Surat Masuk: {surat.kode_tracking}"
    
    # Path absolut menuju sistem (sesuaikan domain/IP saat deploy)
    link_surat = f"http://127.0.0.1:8000/detail-surat/{surat.uuid}/"
    
    nama_pengirim = pengirim_user.get_full_name() or pengirim_user.username if pengirim_user else "Sistem / Pemohon"
    
    pesan_teks = f"""
Yth. Bapak/Ibu Pejabat / Staf DPRD Kabupaten Garut,

Terdapat permohonan audiensi yang diteruskan dan membutuhkan tindakan Anda:

- Kode Tracking   : {surat.kode_tracking}
- Nama Pemohon    : {surat.nama_pemohon}
- Perihal         : {surat.perihal}
- Diteruskan Oleh : {nama_pengirim}
- Status Tahap    : {surat.get_status_display()}
- Catatan         : "{catatan}"

Silakan masuk ke tautan berikut untuk memeriksa detail surat dan memproses disposisi:
{link_surat}

---
Pesan ini dikirim secara otomatis oleh Sistem E-AUDIENSI DPRD Kabupaten Garut.
    """

    try:
        send_mail(
            subject=subject,
            message=pesan_teks,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=email_tujuan,
            fail_silently=True # Mencegah error crash jika jaringan/SMTP bermasalah
        )
    except Exception as e:
        print(f"Gagal mengirim notifikasi email: {e}")