from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from reversion.admin import VersionAdmin
from reversion_compare.admin import CompareVersionAdmin

from DMS.models import *


class DocumentAdmin(CompareVersionAdmin):
    list_display = ['name', ]


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email',)

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("email", "first_name", "last_name", "last_login")
    ordering = ("email", "first_name", "last_name", "last_login")
    # refine the fields

    fieldsets = (
        (None, {'fields': (
        'email', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'groups',
        'user_permissions', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
            'email', 'password', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'groups',
            'user_permissions', 'last_login')}
         ),
    )

    search_fields = ('first_name', 'last_name', 'email',)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Document, DocumentAdmin)
