from datetime import date

from django.db import migrations


def create_missing_availability(apps, schema_editor):
    Room = apps.get_model('travel', 'Room')
    Availability = apps.get_model('travel', 'Availability')
    for room in Room.objects.all():
        Availability.objects.get_or_create(
            room=room,
            check_in=date(2026, 7, 15),
            check_out=date(2026, 7, 22),
            defaults={'rooms_available': 5},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('travel', '0006_backfill_default_rooms'),
    ]

    operations = [
        migrations.RunPython(create_missing_availability, migrations.RunPython.noop),
    ]
