---
title: coding 自动更新到 github
draft: true
---


公司屏蔽了 Github，Gitee 又限制太多，只能通过 Coding 提交代码。配合持续集成功能，可以自动将代码同步到 Github。

如果项目左侧菜单栏没有“持续集成”按钮，可以通过“自定义菜单栏”启用这个选项。

进入“持续集成”→“构建计划”，点击“创建构建计划”

向 Github 提交代码，需要 ssh 证书或者输入密码，这两个东西放在 coding CI 脚本里都不合适，因此需要创建一个 github personal access token。
