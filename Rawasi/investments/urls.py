from django.urls import path
from . import views

app_name = 'investments'

urlpatterns = [
    path('add_investment_opportunity/', views.add_investment_opportunity, name='add_investment_opportunity'),
    path('detail/<id>/', views.investment_opportunity_detail, name='investment_opportunity_detail'),
    path('investment_opportunity/delete/<id>/', views.delete_investment_opportunity, name='delete_investment_opportunity'),
    path('update/<id>/', views.update_investment_opportunity, name='update_investment_opportunity'),
    path('add-voting/', views.add_voting, name='add_voting'),
]

