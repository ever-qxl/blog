from django.db import models

# Create your models here.


class User(models.Model):
    username = models.CharField(verbose_name='用户名', max_length=11, primary_key=True)
    nickname = models.CharField(verbose_name='昵称', max_length=30)
    email = models.EmailField(verbose_name='邮箱', max_length=50)
    password = models.CharField(verbose_name='密码', max_length=40)
    sign = models.CharField(verbose_name='个人签名', max_length=50)
    info = models.CharField(verbose_name='个人描述', max_length=150)
    avatar = models.ImageField(upload_to='avatar/')
    class Meta:
        db_table = 'users'