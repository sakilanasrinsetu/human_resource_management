from django.contrib import admin
from user.models import *

# Register your models here.


class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['id','first_name', 'last_name', 'email','phone', 'is_active']

    class Meta:
        model = UserAccount
admin.site.register(UserAccount, UserAccountAdmin)