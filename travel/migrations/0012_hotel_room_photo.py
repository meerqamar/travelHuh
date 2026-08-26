from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('travel', '0011_pakistan_market_hotels'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='image',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='hotel',
            name='photo',
            field=models.ImageField(blank=True, upload_to='hotels/'),
        ),
        migrations.AlterField(
            model_name='room',
            name='image',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='room',
            name='photo',
            field=models.ImageField(blank=True, upload_to='rooms/'),
        ),
    ]
