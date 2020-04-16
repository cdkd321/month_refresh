# encoding utf-8

from django.conf.urls import url

from goods.views import GoodsView, GoodsDetail, ListView

urlpatterns = [
    url(r'^index$', GoodsView.as_view(), name='index'),
    url(r'^goods/(?P<goods_id>\d+)$', GoodsDetail.as_view(), name='detail'),
    url(r'^list/(?P<type_id>\d+)/(?P<page>\d+)$', ListView.as_view(), name='list'), # 列表页
]
