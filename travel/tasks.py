from celery import shared_task

from .inventory import expire_pending_bookings


@shared_task(name='travel.tasks.cleanup_expired_bookings')
def cleanup_expired_bookings():
    return expire_pending_bookings()
