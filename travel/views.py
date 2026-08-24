from django.http import JsonResponse
from django.shortcuts import render

from .models import Booking, Hotel, Passenger, Room


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
        try:
            room = Room.objects.select_related('hotel').get(pk=request.POST.get('room_id'))
        except (Room.DoesNotExist, TypeError):
            return JsonResponse({'error': 'The selected room is no longer available.'}, status=400)
        total_price = room.price_per_person * 2

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

        booking = Booking.objects.create(hotel=room.hotel, room=room, total_price=total_price)
        Passenger.objects.create(booking=booking, **passenger_fields)
        return JsonResponse({'booking_id': booking.pk, 'message': 'Booking confirmed.'})

    return render(request, 'checkout.html')
