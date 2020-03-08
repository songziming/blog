---
title: Django+MySQL搭建API服务器遇到的坑
date: 2020-03-07
---

### API server

这是一个API服务，客户端通过HTTP请求与服务器通信，request与response基本上都是JSON格式。因此，在这个应用中，不会涉及到模板渲染。

### 并发模型

django服务一般都通过uWSGI协议部署，例如gunicorn。部署之后，会启动若干worker线程，同时处理接收到的用户请求。如果在view handler中需要访问数据库，就会遇到并发问题。

Django本身是可重入的，但我们仍需要保证数据库操作是安全的。

默认配置下，Django使用auto commit mode，也就是每次query自动执行


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
