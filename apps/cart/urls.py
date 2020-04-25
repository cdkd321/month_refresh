# encoding utf-8

from django.conf.urls import url
from cart.views import CartAddView, CartInfoView, CartUpdateView, CartDeleteView


urlpatterns = [
    # 商品详情 购物车添加
    url(R'^add$', CartAddView.as_view(), name='add'),
    # 购物车列表
    url(R'^$', CartInfoView.as_view(), name='show'),
    # 更新购物车数量
    url(r'^update$', CartUpdateView.as_view(), name='update'),
    # 删除购物车指定商品
    url(r'^delete$', CartDeleteView.as_view(), name='delete')

]
