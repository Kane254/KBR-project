# bus_app/views.py

import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
from django.contrib import messages
from decimal import Decimal
from django.http import HttpResponse
from django.http import HttpResponse # Import HttpResponse for generic error response

from .models import Bus, Seat, Booking
from .forms import CustomUserCreationForm, CustomAuthenticationForm

logger = logging.getLogger(__name__)


# --- Authentication Views ---

def register_view(request):
    """Handles user registration and sends a welcome email."""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful. Welcome!")


            # --- Send Welcome Email ---

            subject = "Welcome to BusBook!"
            message = (
                f"Hello {user.username},\n\n"
                f"Thank you for registering with BusBook! We're excited to have you on board.\n"
                f"You can now explore bus routes and book your tickets.\n\n"
                f"Start your journey here: http://127.0.0.1:8000/\n\n" # Adjust URL for deployment
                f"Best regards,\n"
                f"The BusBook Team"
            )
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],

                    fail_silently=False,
                    fail_silently=False, # Set to True in production to avoid crashing on email failure

                )
                messages.info(request, "A welcome email has been sent to your registered email address.")
            except Exception as e:
                logger.error(f"Failed to send welcome email to {user.email}: {e}", exc_info=True)
                messages.warning(request, "Registration successful, but failed to send welcome email.")

            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'bus_app/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username/email or password.")
        else:
            messages.error(request, "Invalid username/email or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'bus_app/login.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('home')

# --- Bus Booking Views ---

def home_view(request):
    buses = Bus.objects.all().order_by('departure_time')
    return render(request, 'bus_app/home.html', {'buses': buses})

@login_required
def bus_detail_view(request, bus_id):

    try:
        bus = get_object_or_404(Bus, id=bus_id)
        seats = Seat.objects.filter(bus=bus).order_by('seat_number')

        if not seats.exists() or seats.count() < bus.capacity:
            with transaction.atomic():
                for i in range(1, bus.capacity + 1):
                    Seat.objects.get_or_create(bus=bus, seat_number=i)
            seats = Seat.objects.filter(bus=bus).order_by('seat_number')

        booked_seat_numbers = set(seats.filter(is_booked=True).values_list('seat_number', flat=True))


    """
       Displays the seat layout for a specific bus and handles seat selection.
       Includes error handling to ensure an HttpResponse is always returned.
       """
    try:
        bus = get_object_or_404(Bus, id=bus_id)
        # Fetch all seats for the bus, ordered by seat number
        seats = Seat.objects.filter(bus=bus).order_by('seat_number')

        # If seats don't exist yet for this bus, create them (for initial setup)
        # This block is crucial after a fresh database, as it populates the seats.
        if not seats.exists() or seats.count() < bus.capacity:
            with transaction.atomic():
                for i in range(1, bus.capacity + 1):
                    # Use get_or_create to avoid creating duplicates if run multiple times
                    Seat.objects.get_or_create(bus=bus, seat_number=i)
            # Re-fetch seats after creation to ensure the 'seats' queryset is up-to-date
            seats = Seat.objects.filter(bus=bus).order_by('seat_number')  # <-- Remove comma

        # Determine which seats are booked
        booked_seat_numbers = set(seats.filter(is_booked=True).values_list('seat_number', flat=True))  # <-- Remove comma

        # Prepare seat data for the template

        seat_layout = []
        for seat in seats:
            seat_layout.append({
                'number': seat.seat_number,
                'is_booked': seat.is_booked,
                'id': seat.id
                'id': seat.id # Pass seat ID for easy lookup in booking

            })

        context = {
            'bus': bus,
            'seat_layout': seat_layout,
            'booked_seat_numbers': booked_seat_numbers,
        }
        return render(request, 'bus_app/bus_detail.html', context)

    except Bus.DoesNotExist:
        messages.error(request, "The requested bus does not exist.")
        return redirect('home')
    except Exception as e:
        # get_object_or_404 raises Http404, which Django handles by default.
        # This block would only be hit if we used .get() and it failed.
        # For robustness, we'll keep the redirect.
        #messages.error(request, "The requested bus does not exist.")
        #return redirect('home')
    except Exception as e:
        # Catch any other unexpected errors during seat creation or data fetching

        logger.error(f"Error in bus_detail_view for bus_id {bus_id}: {e}", exc_info=True)
        messages.error(request, "An unexpected error occurred while loading bus details. Please try again.")
        return redirect('home')


@login_required
@transaction.atomic
def book_seats_view(request, bus_id):
    if request.method == 'POST':
        bus = get_object_or_404(Bus, id=bus_id)
        selected_seat_ids_str = request.POST.get('selected_seat_ids', '')
        # Get new payment details from the form
        payment_method = request.POST.get('final_payment_method')
        phone_number = request.POST.get('final_phone_number')

        # Log payment details (for simulation purposes)
        logger.info(f"User {request.user.username} attempting payment via {payment_method} for phone: {phone_number}")


        if not selected_seat_ids_str:
            messages.error(request, "No seats selected. Please choose at least one seat.")
            return redirect('bus_detail', bus_id=bus.id)

        selected_seat_ids = [int(sid) for sid in selected_seat_ids_str.split(',') if sid.isdigit()]
        selected_seats = Seat.objects.filter(id__in=selected_seat_ids, bus=bus)

        already_booked_seats = selected_seats.filter(is_booked=True)
        if already_booked_seats.exists():
            messages.error(request, "Some of the selected seats are no longer available. Please choose again.")
            return redirect('bus_detail', bus_id=bus.id)

        num_seats_booked = selected_seats.count()
        if num_seats_booked == 0:
            messages.error(request, "No valid seats were selected.")
            return redirect('bus_detail', bus_id=bus.id)

        total_price = Decimal(num_seats_booked) * bus.fare_per_seat
        discount_applied = False
        if num_seats_booked > 5:
            total_price *= Decimal('0.90')
            discount_applied = True

        payment_successful = True # This is the simulation - always true here
        payment_successful = True

        if payment_successful:
            for seat in selected_seats:
                seat.is_booked = True
                seat.save()

            booking = Booking.objects.create(
                user=request.user,
                bus=bus,
                total_price=total_price,
                discount_applied=discount_applied,

                payment_status='COMPLETED' # Payment is "completed" after simulation

                payment_status='COMPLETED'
            )
            booking.booked_seats.set(selected_seats)

            subject = f"Your Bus Booking Confirmation - {bus.name}"
            seat_numbers = booking.get_booked_seat_numbers()
            message = (
                f"Hello {request.user.username},\n\n"
                f"Your booking for bus '{bus.name}' on route '{bus.route}' "
                f"departing at {bus.departure_time.strftime('%Y-%m-%d %H:%M')} has been confirmed!\n\n"
                f"Seats Booked: {seat_numbers}\n"
                f"Number of Seats: {num_seats_booked}\n"
                f"Total Price: Ksh {total_price:.2f}\n"
            )
            if discount_applied:
                message += "A 10% discount was applied to your booking!\n"

            message += f"\nPayment Method: {payment_method}\n" # Include payment method in email
            message += f"Phone Number: {phone_number}\n" # Include phone number in email
            message += "\nThank you for choosing our service!"

            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [request.user.email],
                    fail_silently=False,
                )
                messages.success(request, "Booking successful! A confirmation email has been sent.")
            except Exception as e:
                messages.warning(request, f"Booking successful, but failed to send confirmation email: {e}")

            return render(request, 'bus_app/booking_success.html', {
                'booking': booking,
                'bus': bus,
                'selected_seats': selected_seats,
                'num_seats_booked': num_seats_booked,
                'total_price': total_price,
                'discount_applied': discount_applied
            })
        else:
            messages.error(request, "Payment failed. Please try again.")
            return redirect('bus_detail', bus_id=bus.id)
    else:
        return redirect('home')

@login_required
def my_bookings_view(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    context = {
        'bookings': bookings
    }
    return render(request, 'bus_app/my_bookings.html', context)

def about_us_view(request):

    return render(request, 'bus_app/about_us.html')

def contact_us_view(request):
    return render(request, 'bus_app/contact_us.html')


def available_bus_view(request):
    """Renders the Available Buses page."""
    buses = Bus.objects.all().order_by('departure_time')
    return render(request, 'bus_app/available_bus.html', {'buses': buses})    

    """Renders the About Us page."""
    return render(request, 'bus_app/about_us.html')

def contact_us_view(request):
    """Renders the Contact Us page."""
    return render(request, 'bus_app/contact_us.html')


