
# encoding utf-8
# 校验是否登录
from django.contrib.auth.decorators import login_required


class LoginRequiredView(object):

    @classmethod
    def as_view(cls, **initkargs):
        return login_required(super(LoginRequiredView, cls).as_view(**initkargs))

