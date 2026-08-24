from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def search_results(request):
    return render(request, 'search_results.html')


def hotel_detail(request):
    return render(request, 'hotel_detail.html')


def checkout(request):
    return render(request, 'checkout.html')
