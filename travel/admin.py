from django.contrib import admin

from .models import Availability, Booking, Destination, Hotel, Passenger, Review, Room, Shortlist


class RoomInline(admin.StackedInline):
    model = Room
    extra = 1
    fields = ('name', 'photo', 'board_basis', 'price_per_person', 'max_guests', 'features', 'image')


class AvailabilityInline(admin.TabularInline):
    model = Availability
    extra = 1


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'has_photo')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    
    @admin.display(boolean=True, description='Photo')
    def has_photo(self, obj):
        return bool(obj.photo)


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination', 'rating', 'price_per_person', 'board_basis', 'has_photo')
    search_fields = ('name', 'destination__name')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [RoomInline]
    fields = (
        'name', 'slug', 'destination', 'photo', 'rating', 'price_per_person',
        'board_basis', 'facilities', 'latitude', 'longitude', 'image',
    )

    @admin.display(boolean=True, description='Photo')
    def has_photo(self, obj):
        return bool(obj.photo)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotel', 'board_basis', 'price_per_person', 'max_guests', 'has_photo')
    list_filter = ('board_basis', 'hotel')
    search_fields = ('name', 'hotel__name')
    inlines = [AvailabilityInline]
    fields = ('hotel', 'name', 'photo', 'board_basis', 'price_per_person', 'max_guests', 'features', 'image')

    @admin.display(boolean=True, description='Photo')
    def has_photo(self, obj):
        return bool(obj.photo)


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


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'hotel', 'rating', 'location')
    list_filter = ('rating', 'hotel')
    search_fields = ('author', 'body', 'hotel__name')


@admin.register(Shortlist)
class ShortlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'hotel', 'created_at')
    search_fields = ('user__username', 'hotel__name')
