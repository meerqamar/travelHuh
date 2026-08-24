from django.shortcuts import render

from .models import Hotel


def home(request):
    return render(request, 'home.html')


def search_results(request):
    hotels = Hotel.objects.all()
    destination = request.GET.get('destination', '').strip()
    if destination:
        hotels = hotels.filter(location__icontains=destination)
    return render(request, 'search_results.html', {'hotels': hotels, 'destination': destination})


def hotel_detail(request):
    hotel = Hotel.objects.prefetch_related('rooms').filter(slug='paradise-vista').first()
    return render(request, 'hotel_detail.html', {'hotel': hotel})


def checkout(request):
    return render(request, 'checkout.html')
