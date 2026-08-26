from datetime import date
from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


def seed_hotel_content(apps, schema_editor):
    Hotel = apps.get_model('travel', 'Hotel')
    Review = apps.get_model('travel', 'Review')
    Availability = apps.get_model('travel', 'Availability')

    coords = {
        'paradise-vista': (Decimal('4.175500'), Decimal('73.509300')),
        'sapphire-oasis': (Decimal('34.772000'), Decimal('32.429700')),
        'windmill-bay': (Decimal('36.434900'), Decimal('28.217600')),
    }
    reviews = {
        'paradise-vista': [
            ('Sarah J.', 'London', 5, 'Literally said “Huh?” when I saw the view from my swim-up room. Absolutely stunning resort and the service was world-class.'),
            ('Mark T.', 'Manchester', 5, 'We did not go hungry once. The pools are massive and the food was actually good. What an incredible trip.'),
            ('Elena H.', 'Bristol', 4, 'The spa is a total dream. My only complaint is that I had to leave.'),
        ],
        'sapphire-oasis': [
            ('Priya K.', 'Birmingham', 5, 'Paphos was the surprise of the year. Quiet coves, great all-inclusive spread, and staff who remembered our names.'),
            ('James W.', 'Leeds', 4, 'Brilliant location for exploring Cyprus. Rooms were spotless and the Wi-Fi actually worked.'),
        ],
        'windmill-bay': [
            ('Chloe R.', 'Brighton', 5, 'A boutique hideaway with proper character. Rhodes town is an easy hop and breakfast was outstanding.'),
            ('Omar S.', 'Glasgow', 5, 'Half board here still felt generous. The bay at sunset is the kind of view you send everyone at home.'),
        ],
    }
    facilities = {
        'sapphire-oasis': ['Free WiFi', 'Pool', 'Spa'],
        'windmill-bay': ['Free WiFi', 'Gym', 'Sea view'],
    }

    for hotel in Hotel.objects.all():
        lat_lng = coords.get(hotel.slug)
        if lat_lng:
            hotel.latitude, hotel.longitude = lat_lng
        extra = facilities.get(hotel.slug)
        if extra:
            hotel.facilities = extra
        hotel.save()
        if not hotel.reviews.exists():
            Review.objects.bulk_create([
                Review(hotel=hotel, author=author, location=location, rating=rating, body=body)
                for author, location, rating, body in reviews.get(hotel.slug, [])
            ])

    Availability.objects.all().update(check_in=date(2026, 5, 1), check_out=date(2026, 10, 31))


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0009_booking_expires_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='hotel',
            name='latitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='hotel',
            name='longitude',
            field=models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True),
        ),
        migrations.AddField(
            model_name='booking',
            name='travel_cover',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.CharField(max_length=80)),
                ('location', models.CharField(blank=True, max_length=80)),
                ('rating', models.PositiveSmallIntegerField(default=5)),
                ('body', models.TextField()),
                ('hotel', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='travel.hotel')),
            ],
        ),
        migrations.RunPython(seed_hotel_content, migrations.RunPython.noop),
    ]
