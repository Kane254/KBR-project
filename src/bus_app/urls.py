# bus_app/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views # Import auth views for login/logout

urlpatterns = [
    path('', views.home, name='home'),
    path('buses/', views.bus_list, name='bus_list'),
    path('book/<int:trip_id>/', views.book_trip, name='book_trip'),
    path('my_bookings/', views.my_bookings, name='my_bookings'),

    # Auth URLs
    path('login/', auth_views.LoginView.as_view(template_name='bus_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    # You'd typically add a registration view here too
]