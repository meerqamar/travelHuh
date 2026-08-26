from django import forms
from django.forms import inlineformset_factory
from .models import Hotel, Room, HotelImage, RoomImage

class HotelForm(forms.ModelForm):
    PAYMENT_CHOICES = [
        ('Free cancellation', 'Free cancellation'),
        ('Pay at the hotel', 'Pay at the hotel'),
        ('Pay now', 'Pay now'),
        ('Book without credit card', 'Book without credit card'),
    ]
    SPECIAL_TAGS_CHOICES = [
        ('Great for Groups', 'Great for Groups'),
        ('Pets Allowed', 'Pets Allowed'),
        ('Great for Families', 'Great for Families'),
        ('Workation Friendly', 'Workation Friendly'),
    ]
    
    payment_options = forms.MultipleChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    special_tags = forms.MultipleChoiceField(
        choices=SPECIAL_TAGS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Hotel
        fields = ['name', 'destination', 'property_type', 'photo', 'price_per_person', 'board_basis', 'facilities', 'payment_options', 'location_rating', 'distance_to_center', 'special_tags', 'latitude', 'longitude']
        widgets = {
            'facilities': forms.Textarea(attrs={'rows': 3, 'placeholder': '["Free WiFi", "Pool"]'}),
        }

class RoomForm(forms.ModelForm):
    ROOM_OFFERS_CHOICES = [
        ('Breakfast included', 'Breakfast included'),
        ('Lunch included', 'Lunch included'),
        ('Dinner included', 'Dinner included'),
        ('Early check-in', 'Early check-in'),
    ]
    ROOM_AMENITIES_CHOICES = [
        ('Air conditioning', 'Air conditioning'),
        ('Heating', 'Heating'),
        ('Ironing facilities', 'Ironing facilities'),
        ('Balcony/terrace', 'Balcony/terrace'),
        ('TV', 'TV'),
        ('Refrigerator', 'Refrigerator'),
        ('Internet access', 'Internet access'),
        ('Coffee/tea maker', 'Coffee/tea maker'),
        ('Bathtub', 'Bathtub'),
        ('Washing machine', 'Washing machine'),
        ('Pets allowed in room', 'Pets allowed in room'),
        ('Kitchen', 'Kitchen'),
        ('Private pool', 'Private pool'),
    ]
    
    room_offers = forms.MultipleChoiceField(
        choices=ROOM_OFFERS_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    room_amenities = forms.MultipleChoiceField(
        choices=ROOM_AMENITIES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Room
        fields = ['name', 'photo', 'bed_type', 'number_of_bedrooms', 'max_guests', 'kids_stay_free', 'board_basis', 'price_per_person', 'features', 'room_offers', 'room_amenities']
        widgets = {
            'features': forms.Textarea(attrs={'rows': 3, 'placeholder': '["En-suite", "Balcony"]'}),
        }

HotelImageFormSet = inlineformset_factory(
    Hotel, HotelImage,
    fields=['image', 'category', 'caption'],
    extra=1,
    can_delete=True
)

RoomImageFormSet = inlineformset_factory(
    Room, RoomImage,
    fields=['image', 'category', 'caption'],
    extra=1,
    can_delete=True
)
