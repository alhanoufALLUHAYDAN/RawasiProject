from django.urls import path
from . import views

app_name="investment_fund"

urlpatterns = [
    path('', views.investment_fund_list, name='investment_fund_list'),
    path('create/', views.create_investment_fund, name='create_investment_fund'),
    path('<int:pk>/', views.investment_fund_detail, name='investment_fund_detail'),
    path('<int:pk>/update/', views.update_investment_fund, name='update_investment_fund'),
    path('<int:pk>/delete/', views.delete_investment_fund, name='delete_investment_fund'),
    path('wallet/', views.wallet_view, name="wallet_view"),
]

