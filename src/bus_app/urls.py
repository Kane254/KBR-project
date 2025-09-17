# booking_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('bus/<int:bus_id>/', views.bus_detail_view, name='bus_detail'),
    path('bus/<int:bus_id>/book/', views.book_seats_view, name='book_seats'),
    path('my_bookings/', views.my_bookings_view, name='my_bookings'),
    path('about_us/', views.about_us_view, name='about_us'),       # New URL
    path('contact_us/', views.contact_us_view, name='contact_us'),
    path('available_bus/', views.available_bus_view, name='available_bus'),

]
