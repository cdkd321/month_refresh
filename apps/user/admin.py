from django.contrib import admin
from user.models import User


class UsersAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'email']


# 用户账号的配置
# Register your models here.
admin.site.register(User, UsersAdmin)

