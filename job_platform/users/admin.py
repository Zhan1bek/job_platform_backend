from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, JobSeeker, Employer

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомный UserAdmin, чтобы удобно видеть поля:
    - username, email
    - company, role
    - is_staff, is_superuser и т.д.
    """
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {
            'fields': (
                'first_name', 'last_name',
                'email', 'phone',
                'photo',
                'company',
                'role',
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = (
        'id', 'username', 'email', 'role', 'company', 'is_staff', 'is_superuser'
    )
    list_filter = ('role', 'company', 'is_staff', 'is_superuser')
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ('id',)

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'languages')
    search_fields = ('user__username', 'languages')

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    """
    Если при регистрации Employer действительно создаётся объект
    Employer(user=..., company=...),
    то ты увидишь их здесь.
    """
    list_display = ('id', 'user', 'company')
    search_fields = ('user__username', 'company__name')
