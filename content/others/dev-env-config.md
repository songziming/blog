---
title: 开发环境配置
---

## 修复`git diff`中文乱码

执行命令：

``` sh
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commit.encoding utf-8
git config --global i18n.logoutputencoding utf-8
```

并添加环境变量`LESSCHARSET=utf-8`，如果是Linux则编辑`~/.bashrc`或`~/.zshrc`，Windows则在系统属性中设置。

## GitHub、GitLab使用不同的ssh key

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

## Windows 10

中文输入法设置界面，勾选“使用旧版输入法”。从2004开始，输入法按下`/`会显示顿号，编写代码非常不方便。
