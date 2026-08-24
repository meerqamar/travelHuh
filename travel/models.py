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