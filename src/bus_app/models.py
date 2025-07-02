from django.db import models
from django.contrib.auth.models import User # Django's built-in User model

class Bus(models.Model):
    """Represents a bus with its capacity and route."""
    name = models.CharField(max_length=100)
    capacity = models.IntegerField(help_text="Total number of seats in the bus.")
    route = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    fare_per_seat = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} - {self.route} ({self.departure_time.strftime('%Y-%m-%d %H:%M')})"

    def get_available_seats(self):
        """Returns a list of seat numbers that are not yet booked for this bus."""
        booked_seat_numbers = self.seats.filter(is_booked=True).values_list('seat_number', flat=True)
        all_seat_numbers = set(range(1, self.capacity + 1))
        available_seat_numbers = sorted(list(all_seat_numbers - set(booked_seat_numbers)))
        return available_seat_numbers

class Seat(models.Model):
    """Represents an individual seat on a bus."""
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='seats')
    seat_number = models.IntegerField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('bus', 'seat_number') # A seat number is unique per bus
        ordering = ['seat_number']

    def __str__(self):
        return f"Bus {self.bus.name} - Seat {self.seat_number} ({'Booked' if self.is_booked else 'Available'})"

class Booking(models.Model):
    """Represents a user's booking for one or more seats on a bus."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='bookings')
    booked_seats = models.ManyToManyField(Seat, related_name='bookings')
    booking_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_applied = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=20,
        choices=[('PENDING', 'Pending'), ('COMPLETED', 'Completed'), ('FAILED', 'Failed')],
        default='PENDING'
    )

    def __str__(self):
        return f"Booking by {self.user.username} for {self.bus.name} - {self.booked_seats.count()} seats"

    def get_booked_seat_numbers(self):
        """Returns a comma-separated string of seat numbers for this booking."""
        return ", ".join([str(seat.seat_number) for seat in self.booked_seats.all()])
