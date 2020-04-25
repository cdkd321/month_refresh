from django.contrib import admin
from django.core.cache import cache
from goods.models import GoodsType,IndexPromotionBanner,IndexGoodsBanner,IndexTypeGoodsBanner, GoodsSKU
from goods.models import Goods
# Register your models here.


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        '''新增或更新表中的数据时调用'''
        super().save_model(request, obj, form, change)

        # 发出任务，让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')

    def delete_model(self, request, obj):
        '''删除表中的数据时调用'''
        super().delete_model(request, obj)
        # 发出任务，让celery worker重新生成首页静态页
        from celery_tasks.tasks import generate_static_index_html
        generate_static_index_html.delay()

        # 清除首页的缓存数据
        cache.delete('index_page_data')


class GoodsTypeAdmin(BaseModelAdmin):
    list_display = ['name', 'logo']
    pass


class IndexGoodsBannerAdmin(BaseModelAdmin):
    list_display = ['sku', 'image', 'index']
    pass


class IndexTypeGoodsBannerAdmin(BaseModelAdmin):
    list_display = ['type', 'sku', 'display_type', 'index']
    pass


class IndexPromotionBannerAdmin(BaseModelAdmin):
    list_display = ['name', 'url', 'image', 'index']
    pass


class GoodsSKUAdmin(BaseModelAdmin):
    list_display = ['type', 'name', 'goods', 'price', 'unite', 'desc']
    pass


class GoodsAdmin(BaseModelAdmin):
    list_display = ['name']
    pass


admin.site.register(Goods, GoodsAdmin)
admin.site.register(GoodsSKU, GoodsSKUAdmin)
admin.site.register(GoodsType, GoodsTypeAdmin)
admin.site.register(IndexGoodsBanner, IndexGoodsBannerAdmin)
admin.site.register(IndexTypeGoodsBanner, IndexTypeGoodsBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
