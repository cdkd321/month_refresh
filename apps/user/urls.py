# encoding utf-8

from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from apps.user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, UserSiteView, LogoutView

urlpatterns = [
    url(r'^register$', RegisterView.as_view(), name='register'),
    url(r'^active/(?P<token>.*)$', ActiveView.as_view(), name='active'),
    url(r'^login$', LoginView.as_view(), name='login'),

    # url(r'^logout$', login_required(LogoutView.as_view()), name='logout'),
    # url(r'^order$', login_required(UserOrderView.as_view()), name='order'),
    # url(r'^user$', login_required(UserInfoView.as_view()), name='user'),
    # url(r'^address$', login_required(UserSiteView.as_view()), name='address'),

    url(r'^logout$', LogoutView.as_view(), name='logout'),
    url(r'^order$', UserOrderView.as_view(), name='order'),
    url(r'^user$', UserInfoView.as_view(), name='user'),
    url(r'^address$', UserSiteView.as_view(), name='address'),
]
