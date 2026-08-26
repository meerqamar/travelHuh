from .models import Shortlist


def booking_context(request):
    if request.user.is_authenticated:
        slugs = list(Shortlist.objects.filter(user=request.user).values_list('hotel__slug', flat=True))
        return {'shortlist_count': len(slugs), 'shortlist_slugs': slugs}
    return {'shortlist_count': 0, 'shortlist_slugs': []}
