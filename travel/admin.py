from django.contrib import admin

from .models import Booking, Hotel, Passenger, Room


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'hotel', 'room', 'total_price', 'status', 'created_at')
    list_filter = ('status', 'hotel')
    search_fields = ('hotel__name', 'room__name')


@admin.register(Passenger)
class PassengerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'booking')
    search_fields = ('first_name', 'last_name', 'email')


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'rating', 'price_per_person', 'board_basis')
    search_fields = ('name', 'location')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'board_basis', 'price_per_person')
    list_filter = ('board_basis', 'hotel')
    search_fields = ('name', 'hotel__name')
