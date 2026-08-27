from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F, Prefetch, Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db.models import F, Prefetch, Q
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.views.decorators.http import require_POST
from datetime import date
from datetime import timedelta
from django.utils import timezone

from .inventory import find_availability, restore_availability
from .models import Availability, Booking, Hotel, Passenger, Room, Shortlist, TransportRoute
from .forms import HotelForm, RoomForm, HotelImageFormSet, RoomImageFormSet
from django.utils.text import slugify

TRAVEL_COVER_PRICE = Decimal('2500.00')


def parse_stay(check_in_raw, check_out_raw):
    try:
        start_date = date.fromisoformat(check_in_raw)
        end_date = date.fromisoformat(check_out_raw)
        if end_date <= start_date:
            raise ValueError
    except (TypeError, ValueError):
        start_date = date(2026, 7, 15)
        end_date = date(2026, 7, 22)
    return start_date, end_date


def parse_guests(raw_value, default=2):
    try:
        return max(1, int(raw_value or default))
    except (TypeError, ValueError):
        return default


def stay_nights(start_date, end_date):
    return max(1, (end_date - start_date).days)


def map_embed_url(hotel):
    if hotel.latitude is None or hotel.longitude is None:
        return ''
    lat = float(hotel.latitude)
    lng = float(hotel.longitude)
    pad = 0.08
    return (
        f'https://www.openstreetmap.org/export/embed.html'
        f'?bbox={lng - pad},{lat - pad},{lng + pad},{lat + pad}'
        f'&layer=mapnik&marker={lat},{lng}'
    )


def home(request):
    return render(request, 'home.html', {
        'default_check_in': '2026-07-15',
        'default_check_out': '2026-07-22',
        'featured_hotels': Hotel.objects.all()[:4],
    })


def search_results(request):
    search_type = request.GET.get('type', 'hotel')
    departure = request.GET.get('departure', '').strip()
    
    hotels = Hotel.objects.all()
    destination = request.GET.get('destination', '').strip()
    start_date, end_date = parse_stay(request.GET.get('check_in'), request.GET.get('check_out'))
    check_in = start_date.isoformat()
    check_out = end_date.isoformat()
    nights = stay_nights(start_date, end_date)

    try:
        max_price = int(request.GET.get('max_price', '100000'))
    except ValueError:
        max_price = 100000
    guests = parse_guests(request.GET.get('guests'))
    board = request.GET.get('board', '').strip()
    stars = [int(value) for value in request.GET.getlist('stars') if value.isdigit()]
    facilities = [value.strip() for value in request.GET.getlist('facility') if value.strip()]
    
    # New Advanced Filters
    property_types = request.GET.getlist('property_type')
    payment_options = request.GET.getlist('payment_option')
    special_tags = request.GET.getlist('special_tag')
    room_offers = request.GET.getlist('room_offer')
    room_amenities = request.GET.getlist('room_amenity')
    bed_types = request.GET.getlist('bed_type')
    
    # Numeric / threshold filters
    guest_ratings = [int(v) for v in request.GET.getlist('guest_rating') if v.isdigit()]
    location_ratings = [int(v) for v in request.GET.getlist('location_rating') if v.isdigit()]
    distances = [v for v in request.GET.getlist('distance')]
    bedrooms = [int(v) for v in request.GET.getlist('bedrooms') if v.isdigit()]
    kids_stay_free = request.GET.get('kids_stay_free') == 'on'

    if destination:
        hotels = hotels.filter(Q(destination__name__icontains=destination) | Q(name__icontains=destination))
    hotels = hotels.filter(
        price_per_person__lte=max_price,
        rooms__max_guests__gte=guests,
        rooms__availability__check_in__lte=start_date,
        rooms__availability__check_out__gte=end_date,
        rooms__availability__rooms_available__gte=1,
    )
    if board:
        hotels = hotels.filter(Q(board_basis__iexact=board) | Q(rooms__board_basis__iexact=board))
    if stars:
        rating_filter = Q()
        for star in stars:
            rating_filter |= Q(rating__gte=star, rating__lt=star + 1)
        hotels = hotels.filter(rating_filter)
        
    if guest_ratings:
        hotels = hotels.filter(rating__gte=min(guest_ratings))
    if location_ratings:
        hotels = hotels.filter(location_rating__gte=min(location_ratings))
        
    if property_types:
        hotels = hotels.filter(property_type__in=property_types)
    if bed_types:
        hotels = hotels.filter(rooms__bed_type__in=bed_types)
    if bedrooms:
        hotels = hotels.filter(rooms__number_of_bedrooms__gte=min(bedrooms))
    if kids_stay_free:
        hotels = hotels.filter(rooms__kids_stay_free=True)
        
    # Distance logic (e.g. 'center', '2', '5', '10', '10+')
    if distances:
        distance_filter = Q()
        for d in distances:
            if d == 'center':
                distance_filter |= Q(distance_to_center=0)
            elif d == '2':
                distance_filter |= Q(distance_to_center__lte=2)
            elif d == '5':
                distance_filter |= Q(distance_to_center__lte=5)
            elif d == '10':
                distance_filter |= Q(distance_to_center__lte=10)
            elif d == '10+':
                distance_filter |= Q(distance_to_center__gt=10)
        hotels = hotels.filter(distance_filter)

    for facility in facilities:
        hotels = hotels.filter(facilities__icontains=facility)
    for po in payment_options:
        hotels = hotels.filter(payment_options__icontains=po)
    for tag in special_tags:
        hotels = hotels.filter(special_tags__icontains=tag)
    for ro in room_offers:
        hotels = hotels.filter(rooms__room_offers__icontains=ro)
    for ra in room_amenities:
        hotels = hotels.filter(rooms__room_amenities__icontains=ra)
        
    hotels = hotels.distinct()
    
    # Holiday Package logic: attach transport routes
    transport_routes = {}
    if search_type == 'holiday':
        for hotel in hotels:
            route = TransportRoute.objects.filter(
                destination=hotel.destination, 
                origin__icontains=departure if departure else 'Islamabad'
            ).first()
            if not route:
                route = TransportRoute.objects.filter(destination=hotel.destination).first()
            transport_routes[hotel.id] = route
    return render(request, 'search_results.html', {
        'search_type': search_type,
        'departure': departure,
        'transport_routes': transport_routes,
        'hotels': hotels,
        'destination': destination,
        'check_in': check_in,
        'check_out': check_out,
        'guests': guests,
        'max_price': max_price,
        'nights': nights,
        'board': board,
        'stars': stars,
        'facilities': facilities,
        # pass context for active state
        'property_types': property_types,
        'payment_options': payment_options,
        'special_tags': special_tags,
        'room_offers': room_offers,
        'room_amenities': room_amenities,
        'bed_types': bed_types,
        'guest_ratings': guest_ratings,
        'location_ratings': location_ratings,
        'distances': distances,
        'bedrooms': bedrooms,
        'kids_stay_free': kids_stay_free,
    })


def hotel_detail(request):
    slug = request.GET.get('hotel', 'shangrila-skardu')
    search_type = request.GET.get('type', 'hotel')
    departure = request.GET.get('departure', '').strip()
    
    start_date, end_date = parse_stay(request.GET.get('check_in'), request.GET.get('check_out'))
    guests = parse_guests(request.GET.get('guests'))
    nights = stay_nights(start_date, end_date)
    rooms = Room.objects.filter(max_guests__gte=guests).prefetch_related('availability')
    hotel = get_object_or_404(
        Hotel.objects.prefetch_related(Prefetch('rooms', queryset=rooms), 'reviews'),
        slug=slug,
    )
    rooms_list = list(hotel.rooms.all())
    lowest = min(rooms_list, key=lambda room: room.price_per_person) if rooms_list else None
    selected_room = rooms_list[-1] if rooms_list else None
    
    transport_route = None
    if search_type == 'holiday':
        transport_route = TransportRoute.objects.filter(
            destination=hotel.destination, 
            origin__icontains=departure if departure else 'Islamabad'
        ).first()
        if not transport_route:
            transport_route = TransportRoute.objects.filter(destination=hotel.destination).first()
            
    starting_total = (lowest.price_per_person * guests * nights) if lowest else hotel.price_per_person * guests * nights
    if transport_route:
        starting_total += transport_route.price_per_person * guests
        
    return render(request, 'hotel_detail.html', {
        'search_type': search_type,
        'transport_route': transport_route,
        'hotel': hotel,
        'check_in': start_date,
        'check_out': end_date,
        'guests': guests,
        'nights': nights,
        'starting_total': starting_total,
        'selected_room': selected_room,
        'map_embed_url': map_embed_url(hotel),
    })


def checkout(request):
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please sign in before confirming your booking.'}, status=401)
        try:
            room = Room.objects.select_related('hotel').get(pk=request.POST.get('room_id'))
        except (Room.DoesNotExist, TypeError, ValueError):
            return JsonResponse({'error': 'The selected room is no longer available.'}, status=400)
        guests = parse_guests(request.POST.get('guests'))
        if guests > room.max_guests:
            return JsonResponse({'error': f'This room accommodates a maximum of {room.max_guests} guests.'}, status=400)
        travel_cover = request.POST.get('travel_cover') in {'1', 'true', 'on'}
        check_in, check_out = parse_stay(request.POST.get('check_in'), request.POST.get('check_out'))
        nights = stay_nights(check_in, check_out)
        room_total = room.price_per_person * guests * nights
        
        transport_id = request.POST.get('transport_id')
        transport_route = TransportRoute.objects.filter(pk=transport_id).first() if transport_id else None
        transport_total = (transport_route.price_per_person * guests) if transport_route else Decimal('0.00')
        
        total_price = room_total + transport_total + (TRAVEL_COVER_PRICE if travel_cover else Decimal('0.00'))
        
        availability = find_availability(room, check_in, check_out)
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
            expires_at = timezone.now() + timedelta(minutes=31)
            booking = Booking.objects.create(
                user=request.user,
                hotel=room.hotel,
                room=room,
                check_in=check_in,
                check_out=check_out,
                guests=guests,
                total_price=total_price,
                transport_route=transport_route,
                status='pending',
                expires_at=expires_at,
                travel_cover=travel_cover,
            )
            Passenger.objects.create(booking=booking, **passenger_fields)
        stripe.api_key = settings.STRIPE_SECRET_KEY
        line_items = [{
            'price_data': {
                'currency': 'pkr',
                'product_data': {'name': f'{room.hotel.name} - {room.name}'},
                'unit_amount': int(room_total * 100),
            },
            'quantity': 1,
        }]
        
        if transport_route:
            line_items.append({
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {'name': f'Flight: {transport_route.origin} to {transport_route.destination.name}'},
                    'unit_amount': int(transport_total * 100),
                },
                'quantity': 1,
            })
            
        if travel_cover:
            line_items.append({
                'price_data': {
                    'currency': 'pkr',
                    'product_data': {'name': 'Premium Travel Cover'},
                    'unit_amount': int(TRAVEL_COVER_PRICE * 100),
                },
                'quantity': 1,
            })
        try:
            session = stripe.checkout.Session.create(
                mode='payment',
                line_items=line_items,
                success_url=f'{settings.SITE_URL}/checkout/?payment=success&booking={booking.pk}',
                cancel_url=f'{settings.SITE_URL}/checkout/?payment=cancelled&booking={booking.pk}',
                expires_at=int(expires_at.timestamp()),
                metadata={'booking_id': str(booking.pk), 'travel_cover': str(travel_cover)},
            )
        except stripe.error.StripeError:
            with transaction.atomic():
                Availability.objects.filter(pk=availability.pk).update(rooms_available=F('rooms_available') + 1)
                booking.delete()
            return JsonResponse({'error': 'Payment could not be started. Please try again.'}, status=502)
        booking.stripe_session_id = session.id
        booking.save(update_fields=['stripe_session_id'])
        return JsonResponse({'booking_id': booking.pk, 'checkout_url': session.url, 'message': 'Continue to secure payment.'})

    start_date, end_date = parse_stay(request.GET.get('check_in'), request.GET.get('check_out'))
    guests = parse_guests(request.GET.get('guests'))
    nights = stay_nights(start_date, end_date)
    room = Room.objects.select_related('hotel').filter(pk=request.GET.get('room_id')).first()
    room_total = (room.price_per_person * guests * nights) if room else None
    
    transport_id = request.GET.get('transport_id')
    transport_route = TransportRoute.objects.filter(pk=transport_id).first() if transport_id else None
    transport_total = (transport_route.price_per_person * guests) if transport_route else None
    
    return render(request, 'checkout.html', {
        'check_in': start_date.isoformat(),
        'check_out': end_date.isoformat(),
        'guests': guests,
        'nights': stay_nights(start_date, end_date),
        'room': room,
        'room_total': room_total,
        'transport_route': transport_route,
        'transport_total': transport_total,
        'cover_price': TRAVEL_COVER_PRICE,
    })


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
        restore_availability(booking)
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
    session = event['data']['object']
    booking = Booking.objects.filter(pk=session.get('metadata', {}).get('booking_id'), stripe_session_id=session.get('id')).first()
    if event['type'] == 'checkout.session.completed' and booking and booking.status == 'pending':
        booking.status = 'confirmed'
        booking.payment_status = 'paid'
        booking.expires_at = None
        booking.save(update_fields=['status', 'payment_status', 'expires_at'])
        passenger = booking.passengers.first()
        if passenger:
            send_mail(f'Travel Huh? booking #{booking.pk} confirmed', f'Your booking is confirmed. Reference: #{booking.pk}.', settings.DEFAULT_FROM_EMAIL, [passenger.email])
    elif event['type'] == 'checkout.session.expired' and booking and booking.status == 'pending':
        with transaction.atomic():
            locked = Booking.objects.select_for_update().filter(pk=booking.pk, status='pending').first()
            if locked:
                restore_availability(locked)
                locked.status = 'cancelled'
                locked.payment_status = 'expired'
                locked.save(update_fields=['status', 'payment_status'])
    return JsonResponse({'received': True})

@login_required
def extranet_dashboard(request):
    hotels = request.user.hotels.prefetch_related('rooms').all()
    return render(request, 'extranet/dashboard.html', {'hotels': hotels})

@login_required
def extranet_hotel_create(request):
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES)
        formset = HotelImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.slug = slugify(hotel.name)[:50]
            hotel.save()
            formset.instance = hotel
            formset.save()
            return redirect('extranet-dashboard')
    else:
        form = HotelForm()
        formset = HotelImageFormSet()
    return render(request, 'extranet/hotel_form.html', {'form': form, 'formset': formset})

@login_required
def extranet_hotel_edit(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        formset = HotelImageFormSet(request.POST, request.FILES, instance=hotel)
        if form.is_valid() and formset.is_valid():
            hotel = form.save(commit=False)
            hotel.slug = slugify(hotel.name)[:50]
            hotel.save()
            formset.save()
            return redirect('extranet-dashboard')
    else:
        form = HotelForm(instance=hotel)
        formset = HotelImageFormSet(instance=hotel)
    return render(request, 'extranet/hotel_form.html', {'form': form, 'formset': formset, 'hotel': hotel})

@login_required
def extranet_room_create(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        formset = RoomImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            room = form.save(commit=False)
            room.hotel = hotel
            room.save()
            formset.instance = room
            formset.save()
            return redirect('extranet-dashboard')
    else:
        form = RoomForm()
        formset = RoomImageFormSet()
    return render(request, 'extranet/room_form.html', {'form': form, 'formset': formset, 'hotel': hotel})
