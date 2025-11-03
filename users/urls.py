# accounts/urls.py
from django.urls import path
from .views import register, login_view, me_view, google_auth

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('me/', me_view, name='me'),
    path('google/', google_auth, name='google_auth')
]
