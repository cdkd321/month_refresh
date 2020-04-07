import re

from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings

from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
import time

from user.models import User


def register(request):

    print("register---->")
    print(request.method)
    if request.method == 'GET':
        return render(request, 'register.html')

    # 合法性校验
    user_name = request.POST.get('user_name')
    pwd = request.POST.get('pwd')
    email = request.POST.get('email')

    if not all([user_name, pwd, email]):
        return render(request, 'register.html', {'errmsg': '数据不完整'})

    contract_on = request.POST.get('allow')
    if contract_on != 'on':
        return render(request, 'register.html', {'errmsg': '请同意用户协议'})

    ret = re.match(r"[a-zA-Z_0-9]{4,20}@163\.com$", email)

    print(ret)
    if not ret:
        return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})
    # 检查是否存在相同账号
    res = User.objects.filter(email=email)
    if res.count() > 0:
        return render(request, 'register.html', {'errmsg': '用户已存在'})
    else:
        # 生成用户信息，保存到数据库
        user1 = User.objects.create_user(user_name, email, pwd)
        user1.save()
        return redirect(reverse('goods:index'))


class RegisterView(View):
    '''注册'''

    def get(self, request):
        '''显示注册页面'''
        return render(request, 'register.html')

    def post(self, request):
        '''进行注册处理'''
        # 接收数据
        username = request.POST.get('user_name')
        password = request.POST.get('pwd')
        email = request.POST.get('email')
        allow = request.POST.get('allow')

        # 进行数据校验
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {'errmsg': '数据不完整'})

        # 校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, 'register.html', {'errmsg': '邮箱格式不正确'})

        if allow != 'on':
            return render(request, 'register.html', {'errmsg': '请同意协议'})

        # 校验用户名是否重复
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名不存在
            user = None

        if user:
            # 用户名已存在
            return render(request, 'register.html', {'errmsg': '用户名已存在'})

        # 进行业务处理: 进行用户注册
        user = User.objects.create_user(username, email, password)
        user.is_active = 0
        user.save()

        # 发送激活邮件，包含激活链接: http://127.0.0.1:8000/user/active/3
        # 激活链接中需要包含用户的身份信息, 并且要把身份信息进行加密

        # 加密用户的身份信息，生成激活token
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {'confirm': user.id}
        token = serializer.dumps(info)  # bytes
        token = token.decode()
        # self.send(username, token)
        print("username:%s,email:%s:" % (username, email))
        # 发邮件
        send_register_active_email.delay(email, username, token)

        # 返回应答, 跳转到首页
        return redirect(reverse('user:login'))

    def send(self, nick_name, token):
        msg='<h1>尊敬的%s:<br/>这是您注册账户的激活邮件，<br/></h1><a href="http://127.0.0.1:8000/user/active/%s" ' \
            'target="_blank">点击激活</a>' % (nick_name, token)
        send_mail('注册激活','',settings.EMAIL_FROM,
                  ['593539276@qq.com'],
                  html_message=msg)


class LoginView(View):

    def get(self, request):
        """显示登录页面"""
        if 'user_name' in request.COOKIES:
            username = request.COOKIES.get('user_name')
            check = 'checked'
        else :
            username = ''
            check = ''

        return render(request, 'login.html', {'user_name': username, 'checked': check})

    def post(self, request):
        try:
            username = request.POST.get('username')
            pwd = request.POST.get('pwd')
            remember = request.POST.get('remember')

            user = authenticate(username=username, password=pwd)

            if user is not None:
                # the password verified for the user
                if user.is_active:
                    print("user %s is active."%(username, ))
                    login(request, user)
                    print("login ->")
                    resp = redirect(reverse('goods:index'))
                    if remember == 'on':
                        print("login -> remember on")
                        resp.set_cookie('user_name', username, 7*60*60)
                    else:
                        print("login -> remember off")
                        resp.delete_cookie('user_name')

                    return resp
                else:
                    print("usr not active")
                    return render(request, 'login.html', {'errmsg': '用户还未激活，请先激活'})
            else:
                print("user or password err")
                # the authentication system was unable to verify the username and password
                return render(request, 'login.html', {'errmsg': '用户密码出错'})

        except SignatureExpired:
            return HttpResponse("邮件已经过期")



class ActiveView(View):

    def get(self, request, token):
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            res = serializer.loads(token)
            uid = res['confirm']
            user = User.objects.get(id=uid)
            user.is_active=1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired:
            return HttpResponse("邮件已经过期")




