# booking_app/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class CustomUserCreationForm(UserCreationForm):
    """A custom form for user registration."""
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    


class CustomAuthenticationForm(AuthenticationForm):
    """A custom form for user login."""
    username = forms.CharField(label="Username or Email") # Allow login with email or username

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Try to authenticate with username
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                # If not by username, try to authenticate with email
                try:
                    user = User.objects.get(email=username)
                    self.user_cache = authenticate(self.request, username=user.username, password=password)
                except User.DoesNotExist:
                    pass

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'username': self.username_field.verbose_name},
                )
        return self.cleaned_data

