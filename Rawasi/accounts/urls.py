from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('choose-role/', views.choose_role, name='choose_role'),
    path('register/', views.registration, name='registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('reset-password-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset-password/done/', views.reset_password_done, name='reset_password_done'),
    path('profile/', views.profile, name='profile'),
    path('update/', views.update_profile, name='update_profile'), 
]




