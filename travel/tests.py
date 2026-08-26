from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.utils import timezone

from travel.inventory import expire_pending_bookings
from travel.models import Availability, Booking, Hotel, Room
from travel.views import TRAVEL_COVER_PRICE


class TravelHuhTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('alex', 'alex@example.com', 'password123')
        self.hotel = Hotel.objects.create(
            name='Test Bay Resort',
            slug='test-bay',
            location='Skardu, Gilgit-Baltistan',
            image='images/dest-tenerife.jpg',
            rating=4.5,
            price_per_person=Decimal('500.00'),
            board_basis='Half Board',
            facilities=['Pool', 'Free WiFi'],
            latitude=Decimal('36.434900'),
            longitude=Decimal('28.217600'),
        )
        self.room = Room.objects.create(
            hotel=self.hotel,
            name='Sea View Double',
            image='images/hotel-room.jpg',
            board_basis='Half Board',
            price_per_person=Decimal('40000.00'),
            max_guests=3,
            features=['Balcony'],
        )
        self.availability = Availability.objects.create(
            room=self.room,
            check_in=date(2026, 5, 1),
            check_out=date(2026, 10, 31),
            rooms_available=2,
        )

    def test_search_filters_by_destination_board_and_facility(self):
        response = self.client.get('/search/', {
            'destination': 'Skardu',
            'check_in': '2026-08-01',
            'check_out': '2026-08-08',
            'guests': 2,
            'board': 'Half Board',
            'facility': 'Pool',
        })
        self.assertContains(response, self.hotel.name)
        self.assertContains(response, 'dest-tenerife.jpg')
        self.assertContains(response, 'Total price for 7 nights')

    def test_search_hides_hotels_over_guest_capacity(self):
        response = self.client.get('/search/', {
            'destination': 'Skardu',
            'check_in': '2026-08-01',
            'check_out': '2026-08-08',
            'guests': 8,
        })
        self.assertContains(response, 'No holidays found')

    def test_hotel_detail_uses_selected_dates_and_reviews_map(self):
        response = self.client.get('/hotel/', {
            'hotel': 'test-bay',
            'check_in': '2026-08-01',
            'check_out': '2026-08-08',
            'guests': 2,
        })
        self.assertContains(response, '1 Aug 2026')
        self.assertContains(response, 'openstreetmap.org')
        self.assertContains(response, 'Pool')

    @override_settings(STRIPE_SECRET_KEY='sk_test_123')
    @patch('travel.views.stripe.checkout.Session.create')
    def test_checkout_includes_travel_cover_in_stripe_amount(self, create_session):
        create_session.return_value = MagicMock(id='cs_test', url='https://stripe.test/pay')
        self.client.force_login(self.user)
        response = self.client.post('/checkout/', {
            'room_id': self.room.pk,
            'guests': 2,
            'check_in': '2026-08-01',
            'check_out': '2026-08-08',
            'travel_cover': '1',
            'first_name': 'Alex',
            'last_name': 'Thompson',
            'date_of_birth': '1990-01-01',
            'gender': 'other',
            'email': 'alex@example.com',
            'phone': '07000000000',
            'address': '1 High Street',
        })
        self.assertEqual(response.status_code, 200)
        booking = Booking.objects.get()
        self.assertTrue(booking.travel_cover)
        self.assertEqual(booking.total_price, Decimal('80000.00') + TRAVEL_COVER_PRICE)
        line_items = create_session.call_args.kwargs['line_items']
        self.assertEqual(len(line_items), 2)
        self.assertEqual(line_items[1]['price_data']['unit_amount'], 250000)
        self.assertEqual(line_items[1]['price_data']['currency'], 'pkr')
        self.availability.refresh_from_db()
        self.assertEqual(self.availability.rooms_available, 1)

    def test_expired_pending_booking_releases_inventory(self):
        booking = Booking.objects.create(
            user=self.user,
            hotel=self.hotel,
            room=self.room,
            check_in=date(2026, 8, 1),
            check_out=date(2026, 8, 8),
            guests=2,
            total_price=Decimal('80000.00'),
            status='pending',
            expires_at=timezone.now() - timedelta(minutes=1),
        )
        self.availability.rooms_available = 1
        self.availability.save(update_fields=['rooms_available'])
        released = expire_pending_bookings()
        self.assertEqual(released, 1)
        booking.refresh_from_db()
        self.availability.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(self.availability.rooms_available, 2)

    def test_shortlist_toggle_returns_database_count(self):
        self.client.force_login(self.user)
        saved = self.client.post('/shortlist/toggle/', {'hotel_slug': 'test-bay'})
        self.assertEqual(saved.json()['count'], 1)
        removed = self.client.post('/shortlist/toggle/', {'hotel_slug': 'test-bay'})
        self.assertEqual(removed.json()['count'], 0)
        self.assertFalse(removed.json()['saved'])
