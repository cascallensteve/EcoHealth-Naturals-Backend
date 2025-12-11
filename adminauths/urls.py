from django.urls import path
from .views import (
    admin_signup,
    admin_login,
    admin_logout,
    admin_verify,
    admin_resend_verification,
    list_users,
    delete_user,
)

urlpatterns = [
    path('signup/', admin_signup),
    path('login/', admin_login),
    path('logout/', admin_logout),
    path('verify/', admin_verify),
    path('resend-verification/', admin_resend_verification),
    path('users/', list_users),
    path('users/<int:pk>/delete/', delete_user),
]
