from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Route, Bus, Trip, Booking
from .forms import TripSearchForm, BookingForm
from django.contrib import messages
from django.utils import timezone

def home(request):
    return render(request, 'bus_app/home.html')

def bus_list(request):
    form = TripSearchForm(request.GET)
    trips = Trip.objects.select_related('bus', 'route').filter(departure_time__gte=timezone.now()).order_by('departure_time') # Only future trips

    if form.is_valid():
        origin = form.cleaned_data.get('origin')
        destination = form.cleaned_data.get('destination')
        departure_date = form.cleaned_data.get('departure_date')

        if origin:
            trips = trips.filter(route__origin__icontains=origin)
        if destination:
            trips = trips.filter(route__destination__icontains=destination)
        if departure_date:
            # Filter by date (ignoring time for the search)
            trips = trips.filter(departure_time__date=departure_date)

    context = {
        'form': form,
        'trips': trips
    }
    return render(request, 'bus_app/bus_list.html', context)

@login_required # User must be logged in to book
def book_trip(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    if trip.available_seats <= 0:
        messages.error(request, "Sorry, this trip is fully booked.")
        return redirect('bus_list')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            seat_number = form.cleaned_data['seat_number']

            # Check if seat is already taken for this trip
            if Booking.objects.filter(trip=trip, seat_number=seat_number).exists():
                messages.error(request, f"Seat {seat_number} is already taken for this trip. Please choose another.")
            else:
                booking = form.save(commit=False)
                booking.user = request.user
                booking.trip = trip
                booking.save()

                trip.available_seats -= 1
                trip.save()

                messages.success(request, f"Booking for {trip.route} on {trip.bus.bus_number} (Seat: {seat_number}) successful!")
                return redirect('my_bookings') # Redirect to a page showing user's bookings (you'd create this)
        else:
            messages.error(request, "Please correct the errors in the form.")
    else:
        # Pre-populate the form with the trip ID if needed, though hidden input handles it
        form = BookingForm(initial={'trip': trip.id})

    context = {
        'trip': trip,
        'form': form,
    }
    return render(request, 'bus_app/booking_form.html', context)

@login_required
def my_bookings(request):
    user_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date').select_related('trip__route', 'trip__bus')
    context = {
        'user_bookings': user_bookings
    }
    return render(request, 'bus_app/my_bookings.html', context)

# You'll need Django's built-in authentication for login/logout
# Make sure to configure LOGIN_REDIRECT_URL and LOGOUT_REDIRECT_URL in settings.py
# Example: LOGIN_REDIRECT_URL = '/'
#          LOGOUT_REDIRECT_URL = '/'