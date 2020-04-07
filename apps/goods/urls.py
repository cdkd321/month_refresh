# encoding utf-8

from django.conf.urls import url

from apps.goods.views import GoodsView

urlpatterns = [
    url(r'^$', GoodsView.as_view(), name='index')
]
