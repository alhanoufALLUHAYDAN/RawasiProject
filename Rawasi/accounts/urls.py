from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'accounts'

urlpatterns = [
    path('choose-role/', views.choose_role, name='choose_role'),
    path('investor-registration/', views.investor_registration, name='investor_registration'),
    path('leader-registration/', views.leader_registration, name='leader_registration'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('update/', views.update_profile, name='update_profile'), 
    #path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    #path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    #path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    #path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]


