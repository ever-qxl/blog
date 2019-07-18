# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2019-07-11 16:04
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
        ('topic', '0003_auto_20190711_1604'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=60, verbose_name='留言内容')),
                ('parent_message', models.IntegerField(verbose_name='回复的留言')),
                ('create_time', models.DateTimeField()),
                ('publisher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='user.User')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='topic.Topic')),
            ],
            options={
                'db_table': 'message',
            },
        ),
    ]
