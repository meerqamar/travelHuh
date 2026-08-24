from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search-results'),
    path('hotel/', views.hotel_detail, name='hotel-detail'),
    path('checkout/', views.checkout, name='checkout'),
]
