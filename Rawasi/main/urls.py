from . import views
from django.urls import path

app_name="main"

urlpatterns=[
    path('',views.home_view,name="home_view"),
    path('about/',views.about_view,name="about_view"),
    path('dashboard/fund/',views.fund_dashboard_view,name="fund_dashboard_view"),
    path('dashboard/investor/',views.investor_dashboard_view,name="investor_dashboard_view"),

]