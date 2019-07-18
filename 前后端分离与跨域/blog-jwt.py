import copy
import hmac
import json
import base64
import time


class Jwt():

    def __init__(self):

        pass

    @staticmethod
    def encode(payload, key, exp=300):

        #创建header
        header = {'alg':'HS256', 'typ':'JWT'}
        #创建header json　str
        #separators　第一个参数表示　json串中每个键值对之间　用什么相连， 第二个参数表示 key和value之间用什么相连
        #sort_keys json串按key排序输出
        header_j = json.dumps(header, separators=(',',':'),sort_keys=True)
        #base64 header
        header_bs = Jwt.b64encode(header_j.encode())

        #创建payload部分
        payload = copy.deepcopy(payload)
        #创建过期时间标记
        payload['exp'] = int(time.time() + exp)
        #生成payload的json
        payload_j = json.dumps(payload, separators=(',',':'), sort_keys=True)
        #base64 payload
        payload_bs = Jwt.b64encode(payload_j.encode())

        #生成sign预签串
        to_sign_str = header_bs + b'.' + payload_bs
        #hmac new 中参数 需要用bytes
        if isinstance(key, str):
            #判断key 参数类型，若为字符串，则encode转换至bytes
            key = key.encode()
        hmac_obj = hmac.new(key,to_sign_str, digestmod='SHA256' )
        #获取签名结果
        sign = hmac_obj.digest()
        #生成sign的base64
        sign_bs = Jwt.b64encode(sign)

        return header_bs + b'.' + payload_bs + b'.' + sign_bs

    @staticmethod
    def b64encode(s):
        #替换原生base64中的 = 进行替换
        return base64.urlsafe_b64encode(s).replace(b'=',b'')

    @staticmethod
    def b64decode(bs):
        #将替换=后的base64 补回至原长度
        rem = len(bs) % 4
        bs += b'=' * (4-rem)
        return base64.urlsafe_b64decode(bs)


    @staticmethod
    def decode(token, key):
        '''
        校验token
        :param token:
        :param key:
        :return:
        '''
        #拆解token, 拿出 header_bs , payload_bs , sign
        header_bs, payload_bs, sign = token.split(b'.')
        #判断key的类型
        if isinstance(key, str):
            key = key.encode()
        #重新计算签名
        hm = hmac.new(key, header_bs + b'.' + payload_bs,digestmod='SHA256')
        #base64 签名
        new_sign = Jwt.b64encode(hm.digest())
        if sign != new_sign:
            #当前传过来的token违法, 则raise
            raise JwtError('Your token is valid')
        #token 合法， 判断是否过期
        #base64 deocde payload_bs -> json 串
        payload_j = Jwt.b64decode(payload_bs)
        print(type(payload_j))
        #payload type ?
        payload = json.loads(payload_j.decode())
        #获取过期时间戳
        exp = payload['exp']
        now = time.time()
        #对比两个时间戳是否过期
        if now > exp:
            #token 过期
            raise JwtError('Your token is expired')
        return payload


class JwtError(Exception):
    '''
    自定义异常
    '''

    def __init__(self, error_msg):
        self.error = error_msg

    def __str__(self):
        return '<JwtError error %s>'%(self.error)


if __name__ == '__main__':

    res = Jwt.encode({'username':'guoxiaonao'}, 'abcdef1234')

    print(Jwt.decode(res, 'abcdef'))




