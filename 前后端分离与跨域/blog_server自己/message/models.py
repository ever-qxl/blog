from django.db import models

# Create your models here.
from topic.models import Topic
from user.models import User


class Message(models.Model):
    # topic外键
    topic = models.ForeignKey(Topic)
    content = models.CharField(max_length=60, verbose_name='留言内容')
    # User外键
    publisher = models.ForeignKey(User)
    # 当前内容的父级留言
    parent_message = models.IntegerField(verbose_name='回复的留言')
    create_time = models.DateTimeField()

    class Meta:
        db_table = 'message'
