from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, JobSeeker, Employer

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'interface_language', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff', 'interface_language')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'phone')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'photo', 'interface_language')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    ordering = ('id',)

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'languages')
    search_fields = ('user__username', 'user__email', 'languages')

@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'company')
    search_fields = ('user__username', 'user__email', 'company__name')
