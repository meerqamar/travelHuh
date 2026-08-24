from django.db import models


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


class Booking(models.Model):
    STATUS_CHOICES = [('pending', 'Pending'), ('confirmed', 'Confirmed')]

    hotel = models.ForeignKey(Hotel, on_delete=models.PROTECT)
    room = models.ForeignKey(Room, on_delete=models.PROTECT)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
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