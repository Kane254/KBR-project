from django.db import models

from django.contrib.auth.models import User # For associating bookings with users
from django.core.validators import MinValueValidator

class Route(models.Model):
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    # You might add duration, distance, etc.

    def __str__(self):
        return f"{self.origin} to {self.destination}"

class Bus(models.Model):
    bus_number = models.CharField(max_length=20, unique=True)
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True, related_name='buses')
    # You could add type (e.g., 'Luxury', 'Standard'), amenities, etc.

    def __str__(self):
        return f"{self.bus_number} ({self.route or 'No Route'})"

class Trip(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips_on_route')
    departure_time = models.DateTimeField()
    fare = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    available_seats = models.IntegerField(default=0) # Will be set to bus.capacity on save

    class Meta:
        unique_together = ('bus', 'departure_time') # A bus can only have one trip at a given time

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set available_seats for new trips
            self.available_seats = self.bus.capacity
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Trip {self.id}: {self.route} on {self.bus.bus_number} at {self.departure_time.strftime('%Y-%m-%d %H:%M')}"

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='bookings')
    seat_number = models.CharField(max_length=10) # Simple string for now, could be improved
    booking_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('trip', 'seat_number') # A seat can only be booked once per trip

    def __str__(self):
        return f"Booking {self.id} by {self.user.username} for {self.trip.route} (Seat: {self.seat_number})"

