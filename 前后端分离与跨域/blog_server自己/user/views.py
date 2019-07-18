import json
import hashlib
import time

import jwt
from django.shortcuts import render
from django.http import JsonResponse

from btoken.views import make_token
from tools.login_decorator import loging_check
from . import models


# Create your views here.

@loging_check('PUT')
def users(request, username=None):
    if request.method == 'GET':

        if username:
            try:
                user = models.User.objects.get(username=username)
            except models.User.DoesNotExist:
                user = None
            if not user:
                result = {'code': 208, 'error': 'The user is not existed'}
                return JsonResponse(result)
            # 判断查询字符串
            if request.GET.keys():
                data = {}
                for k in request.GET.keys():
                    if hasattr(user, k):
                        data[k] = getattr(user, k)
                result = {'code': 200, 'username': username, 'data': data}
                return JsonResponse(result)
            else:
                # 证明指定查询用户全量数据
                result = {'code': 200, 'username': username, 'data': {
                    'info': user.info, 'sign': user.sign,
                    'nickname': user.nickname,
                    'avatar': str(user.avatar)
                }}
                return JsonResponse(result)

        else:
            # 获取全部用户的数据
            all_users = models.User.objects.all()
            print(all_users)
            res = []
            for u in all_users:
                d = {}
                d['username'] = u.username
                d['email'] = u.email
                res.append(d)
            result = {'code': 200, 'data': res}
            return JsonResponse(result)

    elif request.method == 'POST':
        # 获取json数据
        json_str = request.body
        if not json_str:
            result = {'code': 202, 'error': 'Please POST data'}
            return JsonResponse(result)
        # 反序列化json_str
        json_obj = json.loads(json_str)
        username = json_obj.get('username')
        email = json_obj.get('email')
        password1 = json_obj.get('password_1')
        password2 = json_obj.get('password_2')
        if not username:
            result = {'code': 203, 'error': 'Please give me username'}
            return JsonResponse(result)
        if not email:
            result = {'code': 204, 'error': 'Please give me email'}
            return JsonResponse(result)
        if not password1 or not password2:
            result = {'code': 205, 'error': 'Please give me password'}
            return JsonResponse(result)
        if password1 != password2:
            result = {'code': 206, 'error': 'The password is wrong'}
            return JsonResponse(result)
        # 检查用户是否存在

        old_user = models.User.objects.filter(username=username)
        if old_user:
            result = {'code': 207, 'error': 'The username is existed'}
            return JsonResponse(result)
        h_p = hashlib.sha1()
        h_p.update(password1.encode())
        try:
            models.User.objects.create(username=username, nickname=username, email=email, password=h_p.hexdigest())
        except Exception as e:
            print('User create error is %s' % e)
            result = {'code': 207, 'error': 'The username is existed'}
            return JsonResponse(result)

        # make_token
        token = make_token(username)
        result = {'code': 200, 'username': username, 'data': {'token': token.decode()}}
        return JsonResponse(result)

    elif request.method == 'PUT':
        # print(dir(request))

        user= request.user
        # print(user)
        json_str = request.body
        # 判断前端是否给了json串
        if not json_str:
            result = {'code': 202, 'error': 'Please Give Data'}
            return JsonResponse(result)
        json_obj = json.loads(json_str)
        nickname = json_obj.get('nickname')
        # 昵称不能为空
        if not nickname:
            result = {'code': 209, 'error': 'Please Give nickname'}
            return JsonResponse(result)

        sign = json_obj.get('sign', '')
        info = json_obj.get('info', '')
        user.sign = sign
        user.info = info
        user.nickname = nickname
        user.save()
        result = {'code': 200, 'username': username}
        return JsonResponse(result)

@loging_check('POST')
def user_avatar(request, username):
    """
    上传文件思路:
    1.前端 form 提交方法为post,并且content-type要改成multipart/form-data
    2.后端只要拿到post提交,requset.FILES['avatar']
    #

    """
    # 当前必须是POST提交
    if not request.method == 'POST':
        result = {'code': 210, 'error': 'Please use POST'}
        return JsonResponse(result)
    users = models.User.objects.filter(username=username)
    if not users:
        result = {'code': 208, 'error': 'The user not existed'}
        return JsonResponse(result)
    if request.FILES.get('avatar'):
        users[0].avatar = request.FILES['avatar']
        users[0].save()
        result = {'code': 200, 'username': username}
        return JsonResponse(result)
    else:
        result = {'code': 211, 'error': 'give me avatar'}
        return JsonResponse(result)
