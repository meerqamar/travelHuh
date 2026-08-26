from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Availability, Booking


def find_availability(room, check_in, check_out, available_only=True):
    if not room or not check_in or not check_out:
        return None
    slots = Availability.objects.filter(room=room)
    if available_only:
        slots = slots.filter(rooms_available__gt=0)
    return (
        slots.filter(check_in=check_in, check_out=check_out).first()
        or slots.filter(check_in__lte=check_in, check_out__gte=check_out).first()
    )


def restore_availability(booking):
    slot = find_availability(booking.room, booking.check_in, booking.check_out, available_only=False)
    if slot:
        Availability.objects.filter(pk=slot.pk).update(rooms_available=F('rooms_available') + 1)


def expire_pending_bookings():
    expired_ids = list(
        Booking.objects.filter(
            status='pending',
            expires_at__isnull=False,
            expires_at__lte=timezone.now(),
        ).values_list('pk', flat=True)
    )
    released = 0
    for pk in expired_ids:
        with transaction.atomic():
            booking = Booking.objects.select_for_update().filter(pk=pk, status='pending').first()
            if not booking:
                continue
            restore_availability(booking)
            booking.status = 'cancelled'
            booking.payment_status = 'expired'
            booking.save(update_fields=['status', 'payment_status'])
            released += 1
    return released
