from django.shortcuts import render,redirect
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.views.generic import View
from django.http import HttpResponse
from django.conf import settings

from goods.models import GoodsSKU
from celery_tasks.tasks import send_register_active_email
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
import re
import time

from user.models import User
from user.models import Address

from utils.login_remix import LoginRequiredView
from django_redis import get_redis_connection

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

                    next_page = request.GET.get('next', reverse('goods:index'))

                    resp = redirect(next_page)
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


class LogoutView(View):

    def get(self, request):
        """显示登录退出页面"""

        # 清除用户的session信息
        logout(request)

        return render(request, 'login.html')


# 激活账户连接处理
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


# 用户中心-个人信息
class UserInfoView(LoginRequiredView, View):
    '''用户中心-信息页'''

    def get(self, request):
        '''显示'''
        # Django会给request对象添加一个属性request.user
        # 如果用户未登录->user是AnonymousUser类的一个实例对象
        # 如果用户登录->user是User类的一个实例对象
        # request.user.is_authenticated()

        # 获取用户的个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户的历史浏览记录
        # from redis import StrictRedis
        # sr = StrictRedis(host='172.16.179.130', port='6379', db=9)
        con = get_redis_connection('default')

        history_key = 'history_%d' % user.id

        # 获取用户最新浏览的5个商品的id
        sku_ids = con.lrange(history_key, 0, 4)  # [2,3,1]

        # 从数据库中查询用户浏览的商品的具体信息
        # goods_li = GoodsSKU.objects.filter(id__in=sku_ids)
        #
        # goods_res = []
        # for a_id in sku_ids:
        #     for goods in goods_li:
        #         if a_id == goods.id:
        #             goods_res.append(goods)

        # 遍历获取用户浏览的商品信息
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        # 组织上下文
        context = {'page': 'user',
                   'address': address,
                   'goods_li': goods_li}

        # 除了你给模板文件传递的模板变量之外，django框架会把request.user也传给模板文件
        return render(request, 'user_center_info.html', context)


# 用户中心，订单列表
class UserOrderView(LoginRequiredView, View):

    def get(self, request):
        return render(request, 'user_center_order.html', {'page': 'order'})


# 用户中心，收货地址
class UserSiteView(LoginRequiredView, View):

    def get(self, request):
        user = request.user
        address = Address.objects.get_default_address(user)
        print("address: ", address)
        return render(request, 'user_center_site.html', {'page': 'address', 'address':address})

    def post(self, request):
        '''地址的添加'''
        # 接收数据
        receiver = request.POST.get('receiver')
        addr = request.POST.get('addr')
        zip_code = request.POST.get('zip_code')
        phone = request.POST.get('phone')

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, 'user_center_site.html', {'errmsg': '数据不完整'})

        # 校验手机号
        if not re.match(r'^1[3|4|5|7|8][0-9]{9}$', phone):
            return render(request, 'user_center_site.html', {'errmsg': '手机格式不正确'})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认收货地址，否则作为默认收货地址
        # 获取登录用户对应User对象
        user = request.user

        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None

        address = Address.objects.get_default_address(user)

        if address:
            is_default = False
        else:
            is_default = True

        print('is_default', is_default)

        # 添加地址
        Address.objects.create(user=user,
                               receiver=receiver,
                               addr=addr,
                               zip_code=zip_code,
                               phone=phone,
                               is_default=is_default)

        # 返回应答,刷新地址页面
        return redirect(reverse('user:address'))  # get请求方式







