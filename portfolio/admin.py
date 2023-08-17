
from django.contrib import admin

# Register your models here.
from django.contrib.auth.models import User,Group

# admin.site.register(SGD_JBE_component_ss_team)
from django.utils.html import format_html
from portfolio.models import *
from django.contrib.auth.admin import UserAdmin
admin.site.unregister(User)
@admin.register(User)
class Usersmod(UserAdmin):
    list_display=(
        "username",
        "first_name",
        "last_name",
        "email",
        "is_staff",
        "is_active",
        "is_superuser",
        'access',        
                )

    def access(self, obj):
        return format_html(f'<a href="/login_via_admin/user/{obj.id}">Login Securely</a>')
    access.allow_tags = True
    access.short_description = 'Login Access'

