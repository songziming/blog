---
title: "Python 虚拟环境管理器 virtualenv"
category: "工具"
tags: ["linux", "python"]
---

virtualenv 是管理 Python 版本的工具，通过它可以实现多个 Python 版本和模块的共存。特别是某些项目需要旧版的 Python 模块，其他项目则需要新版的模块，使用 virtualenv 就能解决这个问题。

virtualenv 也是一个 Python 模块，使用 pip 安装：

``` bash
$ sudo pip install virtualenv
```

### 创建虚拟环境

创建一个虚拟环境，直接用 `virtualenv` 命令就可以：

``` bash
$ virtualenv venv
```

后面的参数表示虚拟环境的名称，在上面的例子中，会在当前目录下创建一个名为 `venv` 的目录，这个目录包含指定版本的 Python
