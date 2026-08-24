from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search_results, name='search-results'),
    path('hotel/', views.hotel_detail, name='hotel-detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('accounts/register/', views.register, name='register'),
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('account/', views.dashboard, name='dashboard'),
    path('account/bookings/<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('payments/stripe/webhook/', views.stripe_webhook, name='stripe-webhook'),
    path('shortlist/toggle/', views.toggle_shortlist, name='toggle-shortlist'),
]
