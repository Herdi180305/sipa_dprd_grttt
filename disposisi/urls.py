from .views import proses_disposisi
from django.urls import path

urlpatterns = [
    path('disposisi/<uuid:uuid>/', proses_disposisi, name='proses_disposisi'),
]