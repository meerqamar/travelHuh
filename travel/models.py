from django.contrib.staticfiles.storage import staticfiles_storage
from django.db import models
from django.contrib.auth.models import User


class PhotoMixin:
    def get_image_url(self):
        photo = getattr(self, 'photo', None)
        if photo:
            return photo.url
        legacy = getattr(self, 'image', '') or ''
        if legacy:
            return staticfiles_storage.url(legacy)
        return staticfiles_storage.url('images/hotel-room.jpg')

    @property
    def image_url(self):
        return self.get_image_url()

class Destination(PhotoMixin, models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    image = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='destinations/', blank=True)

    def __str__(self):
        return self.name


class Hotel(PhotoMixin, models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    destination = models.ForeignKey(Destination, related_name='hotels', on_delete=models.PROTECT, null=True, blank=True)
    image = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='hotels/', blank=True)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    board_basis = models.CharField(max_length=80)
    facilities = models.JSONField(default=list)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name


class Room(PhotoMixin, models.Model):
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    image = models.CharField(max_length=255, blank=True)
    photo = models.ImageField(upload_to='rooms/', blank=True)
    board_basis = models.CharField(max_length=80)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    max_guests = models.PositiveIntegerField(default=2)
    features = models.JSONField(default=list)

    def __str__(self):
        return f'{self.hotel.name} - {self.name}'


class Availability(models.Model):
    room = models.ForeignKey(Room, related_name='availability', on_delete=models.CASCADE)
    check_in = models.DateField()
    check_out = models.DateField()
    rooms_available = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['room', 'check_in', 'check_out'], name='unique_room_availability_period')]

    def __str__(self):
        return f'{self.room} - {self.check_in} to {self.check_out}'


class Booking(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')]

    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='bookings')
    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)
    guests = models.PositiveIntegerField(default=2)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, default='unpaid')
    stripe_session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    travel_cover = models.BooleanField(default=False)

    def __str__(self):
        return f'Booking #{self.pk} - {self.hotel.name}'


class Passenger(models.Model):
    booking = models.ForeignKey(Booking, related_name='passengers', on_delete=models.CASCADE)
    first_name = models.CharField(max_length=80)
    last_name = models.CharField(max_length=80)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    email = models.EmailField()
    phone = models.CharField(max_length=40)
    address = models.TextField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Shortlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shortlists')
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='shortlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['user', 'hotel'], name='unique_user_hotel_shortlist')]


class Review(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='reviews', on_delete=models.CASCADE)
    author = models.CharField(max_length=80)
    location = models.CharField(max_length=80, blank=True)
    rating = models.PositiveSmallIntegerField(default=5)
    body = models.TextField()

    def __str__(self):
        return f'{self.author} on {self.hotel}'