from datetime import date

from django.db import migrations


def create_missing_rooms(apps, schema_editor):
    Hotel = apps.get_model('travel', 'Hotel')
    Room = apps.get_model('travel', 'Room')
    Availability = apps.get_model('travel', 'Availability')

    for hotel in Hotel.objects.all():
        if hotel.rooms.exists():
            continue
        room = Room.objects.create(
            hotel=hotel,
            name=f'{hotel.name} Standard Room',
            image=hotel.image or 'images/hotel-room.jpg',
            board_basis=hotel.board_basis or 'Self Catering',
            price_per_person=hotel.price_per_person,
            features=['Sleeps up to 2', 'Free Wi-Fi'],
        )
        Availability.objects.create(
            room=room,
            check_in=date(2026, 7, 15),
            check_out=date(2026, 7, 22),
            rooms_available=5,
        )


def remove_backfilled_rooms(apps, schema_editor):
    Hotel = apps.get_model('travel', 'Hotel')
    Room = apps.get_model('travel', 'Room')
    for hotel in Hotel.objects.all():
        Room.objects.filter(hotel=hotel, name=f'{hotel.name} Standard Room').delete()


class Migration(migrations.Migration):
    dependencies = [
        ('travel', '0005_booking_payment_status_booking_stripe_session_id_and_more'),
    ]

    operations = [
        migrations.RunPython(create_missing_rooms, remove_backfilled_rooms),
    ]
