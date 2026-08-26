from datetime import date
from decimal import Decimal

from django.db import migrations


HOTELS = {
    'paradise-vista': {
        'name': 'Shangrila Resort Skardu',
        'slug': 'shangrila-skardu',
        'location': 'Skardu, Gilgit-Baltistan',
        'rating': Decimal('4.8'),
        'price_per_person': Decimal('65000.00'),
        'board_basis': 'Half Board',
        'facilities': ['Lake view', 'Free WiFi', 'Restaurant', 'Mountain view', 'Parking'],
        'latitude': Decimal('35.335200'),
        'longitude': Decimal('75.566100'),
        'rooms': [
            {'name': 'Standard Mountain View Room', 'board_basis': 'Half Board', 'price_per_person': Decimal('45000.00'), 'features': ['Sleeps up to 2', 'K2 views', 'Heater & free Wi-Fi']},
            {'name': 'Deluxe Lake View Suite', 'board_basis': 'Half Board', 'price_per_person': Decimal('72000.00'), 'features': ['Private balcony', 'Shangrila lake view', 'Complimentary breakfast']},
        ],
        'reviews': [
            ('Ayesha K.', 'Lahore', 5, 'The lake at sunrise is unreal. Skardu felt like another country, in the best way.'),
            ('Hassan R.', 'Karachi', 5, 'Staff arranged our Deosai day trip perfectly. Rooms were warm and the food was generous.'),
            ('Sana M.', 'Islamabad', 4, 'A proper northern escape. Only wish we had booked more nights.'),
        ],
    },
    'sapphire-oasis': {
        'name': 'Neelum Valley Lodge',
        'slug': 'neelum-valley-lodge',
        'location': 'Keran, Azad Kashmir',
        'rating': Decimal('4.7'),
        'price_per_person': Decimal('32000.00'),
        'board_basis': 'All Inclusive',
        'facilities': ['Free WiFi', 'River view', 'Bonfire', 'Parking'],
        'latitude': Decimal('34.600800'),
        'longitude': Decimal('73.855600'),
        'rooms': [
            {'name': 'River View Twin Room', 'board_basis': 'All Inclusive', 'price_per_person': Decimal('28000.00'), 'features': ['Sleeps up to 2', 'Neelum river view', 'Attached bath']},
            {'name': 'Family Cottage', 'board_basis': 'All Inclusive', 'price_per_person': Decimal('38000.00'), 'features': ['Sleeps up to 4', 'Private lawn', 'Fireplace']},
        ],
        'reviews': [
            ('Fatima Z.', 'Rawalpindi', 5, 'Kashmir was the surprise of our year. The river at Keran is something you keep photographing.'),
            ('Bilal A.', 'Faisalabad', 4, 'Simple, clean, and the all-inclusive meals meant we could just enjoy the valley.'),
        ],
    },
    'windmill-bay': {
        'name': 'Gilgit Serena Stay',
        'slug': 'gilgit-serena-stay',
        'location': 'Gilgit, Gilgit-Baltistan',
        'rating': Decimal('4.6'),
        'price_per_person': Decimal('28000.00'),
        'board_basis': 'Half Board',
        'facilities': ['Free WiFi', 'Gym', 'Restaurant', 'City centre'],
        'latitude': Decimal('35.920200'),
        'longitude': Decimal('74.308000'),
        'rooms': [
            {'name': 'Superior Twin Room', 'board_basis': 'Half Board', 'price_per_person': Decimal('22000.00'), 'features': ['Sleeps up to 2', 'City view', 'Work desk']},
            {'name': 'Executive Suite', 'board_basis': 'Half Board', 'price_per_person': Decimal('35000.00'), 'features': ['Sleeps up to 3', 'Lounge area', 'Mountain outlook']},
        ],
        'reviews': [
            ('Omar S.', 'Peshawar', 5, 'Perfect base for Hunza and Fairy Meadows. Breakfast was outstanding.'),
            ('Nida T.', 'Multan', 4, 'Gilgit town is an easy hop and the hotel team helped with every transfer.'),
        ],
    },
}

HUNZA = {
    'name': 'Hunza View Hotel',
    'slug': 'hunza-view-hotel',
    'location': 'Karimabad, Hunza',
    'image': 'images/dest-tenerife.jpg',
    'rating': Decimal('4.9'),
    'price_per_person': Decimal('42000.00'),
    'board_basis': 'Half Board',
    'facilities': ['Free WiFi', 'Terrace', 'Mountain view', 'Restaurant'],
    'latitude': Decimal('36.316100'),
    'longitude': Decimal('74.665200'),
}


def retarget_pakistan(apps, schema_editor):
    Hotel = apps.get_model('travel', 'Hotel')
    Room = apps.get_model('travel', 'Room')
    Review = apps.get_model('travel', 'Review')
    Availability = apps.get_model('travel', 'Availability')

    for old_slug, data in HOTELS.items():
        hotel = Hotel.objects.filter(slug=old_slug).first() or Hotel.objects.filter(slug=data['slug']).first()
        if not hotel:
            continue
        hotel.name = data['name']
        hotel.slug = data['slug']
        hotel.location = data['location']
        hotel.rating = data['rating']
        hotel.price_per_person = data['price_per_person']
        hotel.board_basis = data['board_basis']
        hotel.facilities = data['facilities']
        hotel.latitude = data['latitude']
        hotel.longitude = data['longitude']
        hotel.save()
        rooms = list(hotel.rooms.all().order_by('id'))
        for room, room_data in zip(rooms, data['rooms']):
            room.name = room_data['name']
            room.board_basis = room_data['board_basis']
            room.price_per_person = room_data['price_per_person']
            room.features = room_data['features']
            room.max_guests = 4 if 'Family' in room_data['name'] else 3 if 'Suite' in room_data['name'] else 2
            room.save()
        hotel.reviews.all().delete()
        Review.objects.bulk_create([
            Review(hotel=hotel, author=author, location=location, rating=rating, body=body)
            for author, location, rating, body in data['reviews']
        ])

    if not Hotel.objects.filter(slug=HUNZA['slug']).exists():
        hunza = Hotel.objects.create(**HUNZA)
        room = Room.objects.create(
            hotel=hunza,
            name='Rakaposhi View Room',
            image='images/hotel-room.jpg',
            board_basis='Half Board',
            price_per_person=Decimal('42000.00'),
            max_guests=2,
            features=['Sleeps up to 2', 'Rakaposhi view', 'Heated room'],
        )
        Availability.objects.create(
            room=room,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 10, 31),
            rooms_available=5,
        )
        Review.objects.create(
            hotel=hunza,
            author='Zara I.',
            location='Islamabad',
            rating=5,
            body='Karimabad at dusk, with Rakaposhi in the window, is the kind of view you send everyone at home.',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0010_hotel_coords_reviews_cover_widen_availability'),
    ]

    operations = [
        migrations.RunPython(retarget_pakistan, migrations.RunPython.noop),
    ]
