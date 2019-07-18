# methods可接受任意参数
import jwt
from django.http import JsonResponse

from user import models

KEY = 'abcd1234'
def loging_check(*methods):
    def login_check(func):
        def wrapper(request, *args, **kwargs):
            # token放在request header ->authorization
            # request.META.get('HTTP_AUTHORIZATION')
            # 判断当前method是否在参数中,如果在,则进行token校验
            # 校验token,pyjwt注意异常检测
            # token校验成功,根据用户名取出用户
            # request.user = user
            token = request.META.get('HTTP_AUTHORIZATION')
            if not methods:
                # 如果没传methods参数, 则直接返回视图
                return func(request, *args, **kwargs)
            else:
                # methods有值
                if request.method not in methods:
                    # 严格判断参数大小写,统一大写
                    # 严格检查methods里的方法必须是[POST,GET,PUT..]
                    # 如果当前请求的方法不在method内,则直接返回视图
                    return func(request, *args, **kwargs)
            if not token or token == 'null':
                result = {'code':107, 'error':'give a token'}
                return JsonResponse(result)
            try:
                res = jwt.decode(token,KEY,algorithms='HS256')

            except jwt.ExpiredSignatureError:
                result = {'code':108, 'error':'please login'}
                return JsonResponse(result)
            except Exception as e:
                print('token error is %s'%e)
                result = {'code':108,'error':'Please login'}
                return JsonResponse(result)
            username = res['username']
            user = models.User.objects.get(username=username)
            request.user = user

            return func(request, *args, **kwargs)
        return wrapper
    return login_check


def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token or token is 'null':
        return None
    try:
        res = jwt.decode(token, KEY, algorithms='HS256')
    except Exception as e:
        print('--get_user_by_request_jwt decode error is %s' % e)
        return None
    username = res['username']
    user = models.User.objects.get(username=username)
    return user






