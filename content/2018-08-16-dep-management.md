---
title: 使用GCC、Makefile管理依赖关系
date:  2018-08-16
---

GCC提供了-M参数，可以自动生成依赖关系，而且这种依赖关系的格式恰好是Makefile语法，可以直接导入到Makefile脚本中。