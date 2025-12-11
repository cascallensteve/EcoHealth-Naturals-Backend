from django.urls import path
from .views import (
    create_consultation,
    list_consultations,
    list_all_consultations,
    delete_consultation,
)

urlpatterns = [
    path('create/', create_consultation, name='create_consultation'),
    path('my-consultations/', list_consultations, name='list_consultations'),
    path('all/', list_all_consultations, name='list_all_consultations'),
    path('<int:pk>/delete/', delete_consultation, name='delete_consultation'),
]
