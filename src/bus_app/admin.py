# bus_app/admin.py

from django.contrib import admin
from .models import Bus, Seat, Booking # Removed 'Route'

@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    """Admin configuration for the Bus model."""
    list_display = ('name', 'route', 'capacity', 'departure_time', 'fare_per_seat')
    list_filter = ('route', 'departure_time')
    search_fields = ('name', 'route')
    ordering = ('departure_time',)

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    """Admin configuration for the Seat model."""
    list_display = ('bus', 'seat_number', 'is_booked')
    list_filter = ('bus', 'is_booked')
    search_fields = ('bus__name', 'seat_number')
    raw_id_fields = ('bus',) # Use raw_id_fields for ForeignKey to improve admin performance

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """Admin configuration for the Booking model."""
    list_display = ('user', 'bus', 'booking_time', 'total_price', 'discount_applied', 'payment_status')
    list_filter = ('payment_status', 'discount_applied', 'bus__name')
    search_fields = ('user__username', 'bus__name', 'booked_seats__seat_number')
    raw_id_fields = ('user', 'bus') # Use raw_id_fields for ForeignKeys
    filter_horizontal = ('booked_seats',) # For ManyToManyField
