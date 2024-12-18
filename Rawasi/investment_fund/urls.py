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
    path('wallet/deposit/', views.deposit_to_wallet, name='deposit_to_wallet'),
    path('wallet/tranfser/<int:pk>/', views.transfer_to_fund, name='transfer_to_fund'),
    path('wallet/withdraw_profit/', views.withdraw_profit, name='withdraw_profit'),
    path('profits/', views.investor_profit_view, name='investor_profit_view'),
    path('profits/withdraw/', views.withdraw_profit, name='withdraw_profit'),
    path('delete/investor/<investor_id>/',views.delete_investor,name="delete_investor")
]

