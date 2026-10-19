from time import timezone
from django.utils import timezone
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from disposisi.models import Disposisi
from disposisi.models import Disposisi
from surat.forms import SuratMasukForm
from .models import SuratAudiensi
from django.contrib import messages
from django.shortcuts import redirect
import random
import string
from datetime import datetime
from django.shortcuts import get_object_or_404
from django_ratelimit.decorators import ratelimit 
from django.db.models import Q
from disposisi.models import Notifikasi

@login_required
def dashboard_overview(request):
    user_profile = request.user.profile
    user_role = user_profile.role
    hari_ini = timezone.now().date()
    
    # Queryset dasar selalu disaring is_deleted=False
    base_qs = SuratAudiensi.objects.filter(is_deleted=False)
    
    if user_role == 'TU':
        qs = base_qs
    elif user_role == 'KOMISI':
        qs = base_qs.filter(
            Q(tujuan_komisi=user_profile.bidang_komisi) & 
            (Q(status='DI_KOMISI') | Q(riwayat_disposisi__pengirim=request.user))
        ).distinct()
    else:
        qs = base_qs.filter(
            Q(status=user_profile.role_status_matching) | 
            Q(riwayat_disposisi__pengirim=request.user)
        ).distinct()

    total_surat = qs.count()
    perlu_tindakan = qs.filter(status=user_profile.role_status_matching).count()
    surat_selesai = qs.filter(status='SELESAI').count()
    aktivitas_terbaru = qs.order_by('-created_at')[:5]

    jadwal_audiensi = base_qs.filter(
        status__in=['DIJADWALKAN', 'SELESAI'],
        tanggal_audiensi__gte=hari_ini
    ).order_by('tanggal_audiensi', 'waktu_audiensi')[:5]

    context = {
        'total_surat': total_surat,
        'perlu_tindakan': perlu_tindakan,
        'surat_selesai': surat_selesai,
        'aktivitas_terbaru': aktivitas_terbaru,
        'jadwal_audiensi': jadwal_audiensi,
    }
    return render(request, 'surat/internal/dashboard.html', context)

def generate_tracking_code():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    
    date_now = datetime.now().strftime('%d%m')
    
    numbers = ''.join(random.choices(string.digits, k=2))
    
    return f"{letters}{date_now}{numbers}"

@login_required
def input_surat(request):
    # Proteksi Role: Hanya TU yang bisa masuk
    if request.user.profile.role != 'TU':
        messages.error(request, "Anda tidak memiliki akses ke halaman ini.")
        return redirect('dashboard')

    if request.method == 'POST':
        form = SuratMasukForm(request.POST)
        if form.is_valid():
            surat = form.save(commit=False)
            
            # Logika Generate Kode Tracking
            surat.kode_tracking = generate_tracking_code()
            
            surat.save()
            messages.success(request, f"Surat berhasil diregistrasi! Kode: {surat.kode_tracking}")
            return redirect('daftar_surat')
    else:
        form = SuratMasukForm()
    
    return render(request, 'surat/internal/input_surat.html', {'form': form})

@login_required
def daftar_surat(request):
    user_profile = request.user.profile
    user_role = user_profile.role
    
    if user_role == 'TU':
        semua_surat = SuratAudiensi.objects.filter(is_deleted=False).order_by('-created_at')
    
    elif user_role == 'KOMISI':
        bidang = user_profile.bidang_komisi
        semua_surat = SuratAudiensi.objects.filter(
            Q(tujuan_komisi=bidang) & 
            (Q(status='DI_KOMISI') | Q(riwayat_disposisi__pengirim=request.user))
        ).filter(is_deleted=False).distinct().order_by('-created_at')
        
    else:
        semua_surat = SuratAudiensi.objects.filter(
            Q(status=user_profile.role_status_matching) | 
            Q(riwayat_disposisi__pengirim=request.user)
        ).filter(is_deleted=False).distinct().order_by('-created_at')

    return render(request, 'surat/internal/daftar_surat.html', {'semua_surat': semua_surat})

def get_role_status(role):
    status_map = {
        'PIM': 'DI_PIMPINAN',
        'SEKWAN': 'DI_SEKWAN',
        'KABAG': 'DI_KABAG',
        'KOMISI': 'DI_KOMISI',
    }
    return status_map.get(role, 'NONE')

@login_required
def edit_surat(request, uuid):
    # Hanya TU yang boleh mengedit data dasar surat
    if request.user.profile.role != 'TU':
        messages.error(request, "Akses ditolak.")
        return redirect('dashboard')
        
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    
    if request.method == 'POST':
        form = SuratMasukForm(request.POST, instance=surat)
        if form.is_valid():
            form.save()
            messages.success(request, "Data surat berhasil diperbarui.")
            return redirect('daftar_surat')
    else:
        form = SuratMasukForm(instance=surat)
        
    return render(request, 'surat/internal/edit_surat.html', {
        'form': form,
        'surat': surat
    })

@login_required
def hapus_surat(request, uuid):
    if request.user.profile.role != 'TU':
        messages.error(request, "Akses ditolak.")
        return redirect('daftar_surat')
        
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    kode = surat.kode_tracking

    # 1. Bersihkan notifikasi terkait surat ini
    Notifikasi.objects.filter(link__contains=str(surat.uuid)).delete()

    # 2. Hapus surat secara permanen (Riwayat Disposisi otomatis terhapus via CASCADE)
    surat.delete()
    
    messages.success(request, f"Surat {kode} berhasil dihapus permanen dari sistem.")
    return redirect('daftar_surat')

@login_required
def cetak_tanda_terima(request, uuid):
    if request.user.profile.role != 'TU':
        messages.error(request, "Akses ditolak.")
        return redirect('daftar_surat')
        
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    
    return render(request, 'surat/internal/cetak_tanda_terima.html', {
        'surat': surat
    })

@login_required
def detail_surat(request, uuid):
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    
    notif_terkait = Notifikasi.objects.filter(
        penerima=request.user, 
        link__contains=str(uuid), 
        is_read=False
    )
    
    if notif_terkait.exists():
        notif_terkait.update(is_read=True)

    context = {
        'surat': surat,
        # 'riwayat': riwayat_disposisi,
    }
    return render(request, 'surat/internal/detail_surat.html', context)

@ratelimit(key='ip', rate='10/m', block=True) # Keamanan: Maksimal 10 percobaan per menit per IP
def home(request):
    if request.method == 'POST':
        kode = request.POST.get('kode_tracking', '').strip().upper()
        try:
            surat = SuratAudiensi.objects.get(kode_tracking=kode, is_deleted=False)
            return redirect('tracking_status', uuid=surat.uuid)
        except SuratAudiensi.DoesNotExist:
            messages.error(request, "Kode tracking tidak ditemukan. Silakan periksa kembali tanda terima Anda.")
            return redirect('home')
            
    return render(request, 'surat/public/home.html')

def tracking_status(request, uuid):
    surat = SuratAudiensi.objects.filter(uuid=uuid, is_deleted=False).first()
    if not surat:
        return redirect('home')
        
    return render(request, 'surat/public/status_detail.html', {'surat': surat})

@login_required
def tentukan_jadwal(request, uuid):
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    
    if request.method == 'POST':
        surat.tanggal_audiensi = request.POST.get('tanggal_audiensi')
        surat.waktu_audiensi = request.POST.get('waktu_audiensi')
        surat.lokasi_audiensi = request.POST.get('lokasi_audiensi')
        
        # Ubah status ke DIJADWALKAN agar TU tahu harus buat surat resmi
        surat.status = 'DIJADWALKAN' 
        surat.save()
        
        Disposisi.objects.create(
            surat=surat,
            pengirim=request.user,
            catatan=f"Jadwal disetujui. Mohon TU segera buatkan surat undangan resmi.",
            status_saat_itu='DIJADWALKAN'
        )
        messages.success(request, "Jadwal disimpan. Berkas dikembalikan ke TU untuk pembuatan surat resmi.")
        return redirect('detail_surat', uuid=surat.uuid)

@login_required
def selesaikan_surat(request, uuid):
    surat = get_object_or_404(SuratAudiensi, uuid=uuid)
    if request.user.profile.role == 'TU':
        surat.status = 'SELESAI'
        surat.save()
        messages.success(request, "Proses audiensi selesai. Pemohon dapat melihat hasil akhir di tracking.")
    return redirect('detail_surat', uuid=surat.uuid)