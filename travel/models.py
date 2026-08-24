from django.db import models
from django.contrib.auth.models import User


class Hotel(models.Model):
    name = models.CharField(max_length=160)
    slug = models.SlugField(unique=True)
    location = models.CharField(max_length=160)
    image = models.CharField(max_length=255)
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
    board_basis = models.CharField(max_length=80)
    facilities = models.JSONField(default=list)

    def __str__(self):
        return self.name


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, related_name='rooms', on_delete=models.CASCADE)
    name = models.CharField(max_length=160)
    image = models.CharField(max_length=255)
    board_basis = models.CharField(max_length=80)
    price_per_person = models.DecimalField(max_digits=8, decimal_places=2)
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
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, default='unpaid')
    stripe_session_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

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