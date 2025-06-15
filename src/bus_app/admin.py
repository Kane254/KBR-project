from django.contrib import admin
from django.contrib import admin
from .models import Route, Bus, Trip, Booking

admin.site.register(Route)
admin.site.register(Bus)
admin.site.register(Trip)
admin.site.register(Booking)

