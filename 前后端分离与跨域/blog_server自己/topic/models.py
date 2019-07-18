from django.db import models

# Create your models here.
from user.models import User


class Topic(models.Model):
    title = models.CharField(verbose_name='文章标题', max_length=50)
    author = models.ForeignKey(User)
    category = models.CharField(verbose_name='分类', max_length=20)
    limit = models.CharField(verbose_name='文章权限', max_length=10)
    create_time = models.DateTimeField(verbose_name='创建时间')
    modified_time = models.DateTimeField(verbose_name='更改时间')
    content = models.TextField(verbose_name='博客的内容')
    introduce = models.CharField(verbose_name='文章简介', max_length=90)

    class Meta:
        db_table = 'topic'
