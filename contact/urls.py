from django.urls import path
from .views import submit_contact, list_contacts, delete_contact

urlpatterns = [
    path('submit/', submit_contact, name='submit_contact'),
    path('all/', list_contacts, name='list_contacts'),
    path('<int:pk>/delete/', delete_contact, name='delete_contact'),
]
