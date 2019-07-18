import datetime
import json

from django.http import JsonResponse
# Create your views here.
from message.models import Message
from tools.login_decorator import loging_check, get_user_by_request
from topic import models


@loging_check('POST', 'DELETE')
def topics(request, author_id=None):
    if request.method == 'POST':
        # 发表博客 必须为登录状态
        # 当前token中认证通过的用户即为作者
        author = request.user
        json_str = request.body
        # 将json串反序列化成python对象
        json_obj = json.loads(json_str)
        title = json_obj.get('title')
        category = json_obj.get('category')
        # 带全部样式的内容-content如加粗颜色等
        content = json_obj.get('content')
        # 纯文本的文章内容-content_text,用来做introducce的截取
        content_text = json_obj.get('content_text')
        # 根据content_text的内容生成文章简介
        introduce = content_text[:30]
        limit = json_obj.get('limit')
        now = datetime.datetime.now()

        if not json_str:
            result = {'code': 302, 'error': 'Please Post Data'}
            return JsonResponse(result)

        if not title:
            result = {'code': 102, 'error': 'Please Give Title'}
            return JsonResponse(result)

        if limit not in ['public', 'private']:
            result = {'code': 303, 'error': 'please give me right limit'}
            return JsonResponse(result)

        if category not in ['tec', 'no-tec']:
            result = {'code': 304, 'error': 'please give me right category'}
            return JsonResponse(result)
        # 存储topic

        models.Topic.objects.create(title=title,
                                    content=content,
                                    limit=limit,
                                    category=category,
                                    author=author,
                                    create_time=now,
                                    modified_time=now,
                                    introduce=introduce)

        result = {'code': 200, 'username': author.username}
        return JsonResponse(result)

    elif request.method == "GET":
        # 获取用户博客列表or具体博客内容
        # 访问当前博客的访问者-visitor
        # 当前博客的博主-author
        visitor = get_user_by_request(request)
        authors = models.User.objects.filter(username=author_id)
        if not authors:
            result = {'code': 305, 'error': 'the current author is not existed'}
            return JsonResponse(result)
        # 当前访问的博主　
        author = authors[0]
        # 对比两者的username是否一致,从而判断当前是否要取private的博客
        visitor_username = None
        if visitor:
            visitor_username = visitor.username
        # 尝试获取t_id,如果有则证明当前请求是获取用户指定ID的博客内容
        t_id = request.GET.get('t_id')
        if t_id:
            # 取指定t_id的博客
            t_id = int(t_id)

            # 博主访问自己博客的标记/True 则表明当前为 博主访问自己的博客 / False 陌生人访问当前博客
            is_self = False

            if visitor_username == author_id:
                # 改变标记
                is_self = True

                # 博主访问自己的博客
                try:
                    author_topic = models.Topic.objects.get(id=t_id)
                except Exception as e:
                    result = {'code': 309, 'error': 'No topic'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = models.Topic.objects.get(id=t_id, limit='public')
                except Exception as e:
                    result = {'code': 309, 'error': 'No topic'}
                    return JsonResponse(result)
                # 生成具体返回
            res = make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)

        else:
            category = request.GET.get('category')
            if category in ['tec', 'no-tec']:
                # 判断category取值范围
                if visitor_username == author_id:
                    # 博主在访问自己的博客,此时获取用户全部权限的博客
                    author_topics = models.Topic.objects.filter(author_id=author_id, category=category)
                else:
                    # 其他访问者在访问当前博客
                    author_topics = models.Topic.objects.filter(author_id=author_id, limit='public', category=category)

            else:
                if visitor_username == author_id:
                    # 博主在访问自己的博客,此时获取用户全部权限的博客
                    author_topics = models.Topic.objects.filter(author_id=author_id)
                else:
                    # 其他访问者在访问当前博客
                    author_topics = models.Topic.objects.filter(author_id=author_id, limit='public')

            res = make_topics_res(author, author_topics)
            return JsonResponse(res)

    elif request.method == 'DELETE':
        author = request.user
        if author.username != author_id:
            result = {'code': 306, 'error': 'You can not do it'}
            return JsonResponse(result)
        # 当token中的用户名和url中的author_id严格一致时,方可执行删除
        topic_id = request.GET.get('topic_id')
        if not topic_id:
            result = {'code': 307, 'error': 'You can not do it !!'}
            return JsonResponse(result)
        try:
            topic = models.Topic.objects.get(id=topic_id)
        except Exception as e:
            print('topic delete error is %s' % e)
            result = {'code': 308, 'error': 'not existed'}
            return JsonResponse(result)
        topic.delete()
        result = {'code': 200}
        return JsonResponse(result)


def make_topics_res(author, author_topics):
    res = {'code': 200, 'data': {}}
    topics_res = []
    for topic in author_topics:
        d = {}
        d['id'] = topic.id
        d['title'] = topic.title
        d['category'] = topic.category
        d['created_time'] = topic.create_time.strftime('%Y-%m-%d %H:%M:%S')
        d['introduce'] = topic.introduce
        d['author'] = author.nickname
        topics_res.append(d)
    res['data']['topics'] = topics_res
    res['data']['nickname'] = author.nickname

    return res


def make_topic_res(author, author_topic, is_self):
    '''
    生成具体博客内容的返回值
    :param author:
    :param author_topic:
    :return:
    '''
    if is_self:
        # 博主访问自己的
        # next
        # 取出ID大于当前博客ID的数据的第一个
        next_topic = models.Topic.objects.filter(id__gt=author_topic.id, author=author).first()
        # last
        # 取出ID小于当前博客ID的数据的最后一个
        last_topic = models.Topic.objects.filter(id__lt=author_topic.id, author=author).last()
    else:
        # 当前访问者不是当前访问博客的博主
        next_topic = models.Topic.objects.filter(id__gt=author_topic.id, limit='public', author=author).first()
        # 取出ID小于当前博客ID的数据的最后一个
        last_topic = models.Topic.objects.filter(id__lt=author_topic.id, limit='public', author=author).last()

    # 判断下一个是否存在
    if next_topic:
        # 下一个博客内容的id
        next_id = next_topic.id
        # 下一个博客内容的title
        next_title = next_topic.title
    else:
        next_id = None
        next_title = None
    # 原理同next
    if last_topic:
        last_id = last_topic.id
        last_title = last_topic.title
    else:
        last_id = None
        last_title = None

    # 生成message返回结构
    # 拿出所有该topic的message并按时间倒叙排序
    all_messages = Message.objects.filter(topic=author_topic).order_by('-create_time')
    # level_msg = {1: [m1, m2, m3], 3, [m4, m5, m6]}
    # messages = [ma_1, mb_3, mc_5]
    msg_list = []
    level1_msg = {}
    m_count = 0
    for msg in all_messages:
        if msg.parent_message:
            # 回复
            level1_msg.setdefault(msg.parent_message, [])
            level1_msg[msg.parent_message].append(
                {'msg_id': msg.id,
                 'publisher': msg.publisher.nickname,
                 'publisher_avatar': str(msg.publisher.avatar),
                 'content': msg.content,
                 'create_time':msg.create_time.strftime('%Y-%m-%d')}
            )


        else:
            # 留言
            m_count += 1
            msg_list.append({'id': msg.id,
                             'content': msg.content,
                             'publisher': msg.publisher.nickname,
                             'publisher_avatar': str(msg.publisher.avatar),
                             'create_time': msg.create_time.strftime('%Y-%m-%d'),
                             'reply':[]})
    for m in msg_list:
        if m['id'] in level1_msg:
            m['reply'] = level1_msg[m['id']]

    result = {'code': 200, 'data': {}}
    result['data']['nickname'] = author.nickname
    result['data']['title'] = author_topic.title
    result['data']['category'] = author_topic.category
    result['data']['create_time'] = author_topic.create_time.strftime('%Y-%m-%d')
    result['data']['content'] = author_topic.content
    result['data']['introduce'] = author_topic.introduce
    result['data']['author'] = author.nickname
    result['data']['next_id'] = next_id
    result['data']['next_title'] = next_title
    result['data']['last_id'] = last_id
    result['data']['last_title'] = last_title
    # 暂时为假数据
    result['data']['messages'] = msg_list
    result['data']['messages_count'] = m_count
    return result
