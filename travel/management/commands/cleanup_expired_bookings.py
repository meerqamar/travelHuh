from django.core.management.base import BaseCommand

from travel.inventory import expire_pending_bookings


class Command(BaseCommand):
    help = 'Release inventory held by expired pending bookings.'

    def handle(self, *args, **options):
        released = expire_pending_bookings()
        self.stdout.write(self.style.SUCCESS(f'Released inventory for {released} expired booking(s).'))
