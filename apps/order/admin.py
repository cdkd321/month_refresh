from django.contrib import admin
from order.models import OrderGoods, OrderInfo

# Register your models here.
# 后台管理类


# 所有订单后台管理类的父类
class BaseModelAdmin(admin.ModelAdmin):
     pass


# 订单管理类
class OrderInfoModelAdmin(BaseModelAdmin):
    pass


# 订单管理类
class OrderModelAdmin(BaseModelAdmin):
    pass


admin.site.register(OrderInfo, OrderInfoModelAdmin)
admin.site.register(OrderGoods, OrderModelAdmin)

