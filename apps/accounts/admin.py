from django.contrib import admin
from django.contrib.auth.models import User

from apps.accounts.forms import UnicodeUserChangeForm, UnicodeUserCreationForm
from .models import UserProfile

current_user_admin = type(admin.site._registry[User])


class UserProfileInline(admin.StackedInline):
    model = UserProfile


class UnicodeUserAdmin(current_user_admin):
    form = UnicodeUserChangeForm
    add_form = UnicodeUserCreationForm
    inlines = [ UserProfileInline, ]

admin.site.unregister(User)
admin.site.register(User, UnicodeUserAdmin)
