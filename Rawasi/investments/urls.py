from django.urls import path
from . import views

app_name = 'investments'

urlpatterns = [
    path('add_investment_opportunity/', views.add_investment_opportunity, name='add_investment_opportunity'),
    path('detail/<id>/', views.investment_opportunity_detail, name='investment_opportunity_detail'),
    path('investment_opportunity/delete/<id>/', views.delete_investment_opportunity, name='delete_investment_opportunity'),
    path('update/<id>/', views.update_investment_opportunity, name='update_investment_opportunity'),
    path('add-voting/', views.add_voting, name='add_voting'),
    path('opportunity-list/', views.opportunity_list, name='opportunity_list'),
    path('vote/<int:id>/', views.vote_on_opportunity, name='vote_on_opportunity'),
    path('buy_opportunity/<opportunity_id>/',views.buy_opportunity, name='buy_opportunity'),
    path('sell_opportunity/<opportunity_id>/',views.sell_opportunity, name='sell_opportunity'),
]

