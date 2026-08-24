from django.contrib import admin

from .models import Availability, Booking, Hotel, Passenger, Room, Shortlist


@admin.register(Shortlist)
class ShortlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'created_at')
    search_fields = ('user__username', 'hotel__name')


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ('room', 'check_in', 'check_out', 'rooms_available')
    list_filter = ('check_in', 'check_out')


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
