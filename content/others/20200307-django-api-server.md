---
title: Django+MySQL搭建API服务器遇到的坑
date: 2020-03-07
---

## 架构设计

这是一个API服务，客户端是Android应用，通过HTTP请求与服务器通信，request与response基本上都是JSON格式。因此，在这个应用中，不会涉及到模板渲染，不能使用cookie，但是需要与数据库通信。

选择Django，主要是因为这个框架的功能比较全面，网上的资料也很多，测试中发现的问题基本上都能找到解决方法。另一个重要的原因是数据库访问，Flask和FastAPI都要使用第三方的SQLAlchemy，但是Django内置了ORM。

## 基于token的登陆验证

没有浏览器，无法使用cookie，因此需要自己实现一套Session机制。登录时，服务器创建一个Session记录，生成一个UUID，并将这条记录保存到数据库。后续调用其他API，都要在request信息中提供这个UUID。

同时，在Session记录中保存最近一次活跃时间，每次访问API的时候都刷新这个值。

也可以将session-id直接保存在User表中，登录成功之后，直接修改这条User记录。这样，可以保证一个用户只能有一个合法的session-id，而且在访问其他API时，使用request-body中提供的session-id可以直接得到用户信息，不需要外键。

## Nginx+gunicorn部署

开发过程中，一般通过`python manage.py runserver`运行dev-server。dev-server有很多缺点，例如对每个request都会启动一个新的线程，如果访问量过大，会耗尽服务器的资源。

django服务一般都通过uWSGI协议部署，例如gunicorn。部署之后，会启动若干worker线程，同时处理接收到的用户请求，相当于多路负载均衡。然而，还要处理burst情况，短时request暴增，我们希望将来不及处理的request缓存下来，等待worker来处理，这个需求可以由Nginx实现。

## 数据库并发访问

gunicorn可以启动多个worker，然而这些worker访问的数据库是同一个。实际运行中，多个view handler可能同时访问数据库，甚至访问同一个数据表。这时，就要保证数据一致性。

默认配置下，Django使用auto commit mode，也就是每次query都会自动执行。例如用`User.objects.get()`获取一个对象，修改对象的字段之后调用`user.save()`更新到数据库，那么就会产生两次数据库访问。这两次数据库操作之间，其他线程可能对相同的记录执行了更新操作。

因此，更新数据库应该采用filter+update机制，也就是通过`User.objects.filter(...).update(...)`，将筛选和更新放在一条SQL语句中执行。只要能通过一条SQL语句完成，数据库就可以保证原子性。另外，善用Django的多表查询功能。否则，只能通过多次数据库查询配合transaction，这会严重影响性能。

其他Django数据库优化建议见[官方文档](https://docs.djangoproject.com/en/3.0/topics/db/optimization/)，当然，能否用好这些trick，数据库设计的好坏也是很关键的。

## Celery执行异步任务

有时候，客户端调用API，会启动一个比较耗时的操作，我们需要启动一个后台线程执行这个操作，view handler则不能后台线程结束，直接返回，这个异步事件机制可以由Celery实现。

``` sh
sudo python3 -m pip install -U celery
sudo apt install rabbitmq-server
```

Celery+Django的组合已经被很多人使用过，稳定性有保证。更重要的是，Celery中运行的任务同样可以访问数据库。

### MySQL server has gone away

这种问题是因为数据库连接长时间不活跃，被MySQL自动断开。要复现也比较容易，首先连接到mysql，将`wait_timeout`设为30，也就是30秒不活跃就自动断开：

``` sql
set global wait_timeout = 30;
```

然后使用`python manage.py shell`引入交互环境，执行一条ORM查询，等待超过30秒，重复查询。应该就会出现“server has gone away”的错误。

Django会在接收到request时新建一个连接，完成处理时断开连接，因此不会有这个问题。这个问题一般出现在手动创建的worker线程。例如通过celery或者线程池，将一些耗时较长的工作放在单独线程中执行。

解决办法就是，每次执行数据库操作之前，先将现有的数据库连接关闭：

``` python
from django.db import close_old_connections

close_old_connections() # 在访问数据库之前执行
```
