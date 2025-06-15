# bus_app/forms.py
from django import forms
from .models import Booking, Route, Trip

class TripSearchForm(forms.Form):
    origin = forms.CharField(max_length=100, required=False, label="From")
    destination = forms.CharField(max_length=100, required=False, label="To")
    departure_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=False)

class BookingForm(forms.ModelForm):
    # This example assumes user picks a seat, in a real app, you'd manage seat availability
    # You might want to make 'seat_number' a CharField for flexibility (e.g. "A1", "12")
    seat_number = forms.CharField(max_length=10, help_text="Enter your desired seat number (e.g., A1, 12).")

    class Meta:
        model = Booking
        fields = ['trip', 'seat_number'] # trip will be set by the view, seat_number by user
        widgets = {'trip': forms.HiddenInput()} # Hide the trip field, as it's passed via URL/context