def notif_context(request):
    if request.user.is_authenticated:
        return {
            'notifikasi_list': request.user.notifikasi.all()[:5],
            'unread_notif_count': request.user.notifikasi.filter(is_read=False).count()
        }
    return {}