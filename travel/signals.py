from datetime import date

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Availability, Hotel, Room


@receiver(post_save, sender=Hotel)
def create_default_room_and_availability(sender, instance, created, **kwargs):
    if not created:
        return

    def ensure_room():
        if instance.rooms.exists():
            return
        room = Room.objects.create(
            hotel=instance,
            name=f'{instance.name} Standard Room',
            image=instance.image or 'images/hotel-room.jpg',
            photo=instance.photo,
            board_basis=instance.board_basis or 'Self Catering',
            price_per_person=instance.price_per_person,
            max_guests=2,
            features=['Sleeps up to 2', 'Free Wi-Fi'],
        )
        Availability.objects.create(
            room=room,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 10, 31),
            rooms_available=5,
        )

    transaction.on_commit(ensure_room)
