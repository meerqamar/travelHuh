from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.db import transaction
from django.views.decorators.http import require_POST

from .models import Availability, Booking, Hotel, Passenger, Room, Shortlist


def home(request):
    return render(request, 'home.html')


def search_results(request):
    hotels = Hotel.objects.all()
    destination = request.GET.get('destination', '').strip()
    if destination:
        hotels = hotels.filter(location__icontains=destination)
    return render(request, 'search_results.html', {'hotels': hotels, 'destination': destination})


def hotel_detail(request):
    slug = request.GET.get('hotel', 'paradise-vista')
    hotel = Hotel.objects.prefetch_related('rooms').filter(slug=slug).first()
    return render(request, 'hotel_detail.html', {'hotel': hotel})


def checkout(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please sign in before confirming your booking.'}, status=401)
        try:
            room = Room.objects.select_related('hotel').get(pk=request.POST.get('room_id'))
        except (Room.DoesNotExist, TypeError):
            return JsonResponse({'error': 'The selected room is no longer available.'}, status=400)
        total_price = room.price_per_person * 2
        check_in = request.POST.get('check_in') or '2026-07-15'
        check_out = request.POST.get('check_out') or '2026-07-22'
        availability = Availability.objects.filter(room=room, check_in=check_in, check_out=check_out, rooms_available__gt=0).first()
        if not availability:
            return JsonResponse({'error': 'This room is not available for the selected dates.'}, status=400)

        passenger_fields = {
            'first_name': request.POST.get('first_name', '').strip(),
            'last_name': request.POST.get('last_name', '').strip(),
            'date_of_birth': request.POST.get('date_of_birth', ''),
            'gender': request.POST.get('gender', ''),
            'email': request.POST.get('email', '').strip(),
            'phone': request.POST.get('phone', '').strip(),
            'address': request.POST.get('address', '').strip(),
        }
        if not all(passenger_fields.values()):
            return JsonResponse({'error': 'Please complete all passenger details.'}, status=400)

        if not settings.STRIPE_SECRET_KEY:
            return JsonResponse({'error': 'Stripe is not configured. Set STRIPE_SECRET_KEY before accepting payments.'}, status=503)

        with transaction.atomic():
            availability = Availability.objects.select_for_update().filter(
                pk=availability.pk,
                rooms_available__gt=0,
            ).first()
            if not availability:
                return JsonResponse({'error': 'This room was just booked by another traveller.'}, status=409)
            availability.rooms_available -= 1
            availability.save(update_fields=['rooms_available'])
            booking = Booking.objects.create(user=request.user, hotel=room.hotel, room=room, check_in=check_in, check_out=check_out, total_price=total_price, status='pending')
            Passenger.objects.create(booking=booking, **passenger_fields)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.create(
                mode='payment',
                line_items=[{'price_data': {'currency': 'gbp', 'product_data': {'name': f'{room.hotel.name} - {room.name}'}, 'unit_amount': int(total_price * 100)}, 'quantity': 1}],
                success_url=f'{settings.SITE_URL}/checkout/?payment=success&booking={booking.pk}',
                cancel_url=f'{settings.SITE_URL}/checkout/?payment=cancelled&booking={booking.pk}',
                metadata={'booking_id': str(booking.pk)},
            )
        except stripe.error.StripeError:
            with transaction.atomic():
                Availability.objects.filter(pk=availability.pk).update(rooms_available=F('rooms_available') + 1)
                booking.delete()
            return JsonResponse({'error': 'Payment could not be started. Please try again.'}, status=502)
        booking.stripe_session_id = session.id
        booking.save(update_fields=['stripe_session_id'])
        return JsonResponse({'booking_id': booking.pk, 'checkout_url': session.url, 'message': 'Continue to secure payment.'})

    return render(request, 'checkout.html')


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        if not username or not email or len(password) < 8:
            return render(request, 'register.html', {'error': 'Use a username, email, and password of at least 8 characters.'})
        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'That username is already in use.'})
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return render(request, 'account.html', {'message': 'Your account is ready.'})
    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        user = authenticate(request, username=request.POST.get('username', ''), password=request.POST.get('password', ''))
        if user:
            login(request, user)
            return render(request, 'account.html', {'message': 'You are signed in.'})
        return render(request, 'login.html', {'error': 'Those login details were not recognised.'})
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return render(request, 'account.html', {'message': 'You are signed out.'})


@login_required
def dashboard(request):
    bookings = Booking.objects.filter(user=request.user).select_related('hotel', 'room').prefetch_related('passengers')
    shortlists = Shortlist.objects.filter(user=request.user).select_related('hotel')
    return render(request, 'dashboard.html', {'bookings': bookings, 'shortlists': shortlists})


@require_POST
def toggle_shortlist(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please sign in to save shortlists.'}, status=401)
    hotel = Hotel.objects.filter(slug=request.POST.get('hotel_slug')).first()
    if not hotel:
        return JsonResponse({'error': 'Hotel not found.'}, status=404)
    shortlist, created = Shortlist.objects.get_or_create(user=request.user, hotel=hotel)
    if not created:
        shortlist.delete()
    return JsonResponse({'saved': created, 'count': Shortlist.objects.filter(user=request.user).count()})


@login_required
@require_POST
def cancel_booking(request, booking_id):
    with transaction.atomic():
        booking = Booking.objects.select_for_update().filter(pk=booking_id, user=request.user).first()
        if not booking:
            return JsonResponse({'error': 'Booking not found.'}, status=404)
        if booking.status == 'cancelled':
            return JsonResponse({'error': 'This booking is already cancelled.'}, status=400)
        if booking.check_in and booking.check_out:
            Availability.objects.filter(room=booking.room, check_in=booking.check_in, check_out=booking.check_out).update(
                rooms_available=F('rooms_available') + 1,
            )
        booking.status = 'cancelled'
        booking.save(update_fields=['status'])
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'message': 'Booking cancelled and room availability restored.'})
    return redirect('dashboard')


@csrf_exempt
@require_POST
def stripe_webhook(request):
    try:
        event = stripe.Webhook.construct_event(request.body, request.headers.get('Stripe-Signature'), settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return JsonResponse({'error': 'Invalid webhook.'}, status=400)
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking = Booking.objects.filter(pk=session.get('metadata', {}).get('booking_id'), stripe_session_id=session.get('id')).first()
        if booking and booking.status == 'pending':
            booking.status = 'confirmed'
            booking.payment_status = 'paid'
            booking.save(update_fields=['status', 'payment_status'])
            passenger = booking.passengers.first()
            if passenger:
                send_mail(f'Travel Huh? booking #{booking.pk} confirmed', f'Your booking is confirmed. Reference: #{booking.pk}.', settings.DEFAULT_FROM_EMAIL, [passenger.email])
    return JsonResponse({'received': True})
