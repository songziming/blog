---
title: ssh config
---

ssh配置文件用的好，可以管理多个密钥文件，登录不同的server使用不同的key。

### GitHub、GitLab使用不同的ssh key

首先生成许多个key：

``` sh
ssh-keygen -t rsa -C "name@email.com"
```

然后编辑`~/.ssh/config`文件：

```
Host github.com
    HostName github.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_github

Host gitlab.com
    HostName gitlab.com
    PreferredAuthentications publickey
    IdentityFile ~/.ssh/id_rsa_gitlab
```

如果登录相同的托管站，但是有多个账号，同样可以再ssh config文件中配置，只要加上`User`字段就可以了：

```
Host github-user1
    HostName        github.com
    User            user1
    IdentityFile    ~/.ssh/id_rsa_user1

Host github-user2
    HostName        github.com
    Port            443
    User            user2
    IdentityFile    ~/.ssh/id_rsa_user2
```

在git仓库下添加remote时：

``` sh
git remote add REMOTE_NAME ssh://HOST_NAME/path/to/repo.git
```

需要把用户名、主机名、端口替换成config文件中指定的host名称。注意前缀`ssh://`一定要加上。


### Windows下

windows下最好使用git客户端自带的ssh，不要使用OpenSSH。同样支持config文件，文件名为`%USERPROFILE%\.ssh\config`。