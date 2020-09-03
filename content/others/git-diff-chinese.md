---
title: git diff显示中文
---

执行命令：

```bash
git config --global core.quotepath false
git config --global gui.encoding utf-8
git config --global i18n.commit.encoding utf-8
git config --global i18n.logoutputencoding utf-8
```

并添加环境变量`LESSCHARSET=utf-8`，如果是Linux则编辑`~/.bashrc`或`~/.zshrc`，Windows则在系统属性中设置。

