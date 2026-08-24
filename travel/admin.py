from django.contrib import admin

from .models import Hotel, Room


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
