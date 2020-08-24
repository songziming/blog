---
title: Linux x64启动过程
date: 2020-03-31
---

参考资料：

- [Linux-Insides/Booting](https://0xax.gitbooks.io/linux-insides/Booting/)

## 引导

Linux不使用Multiboot协议，而是自己发明了一套规则，虽然也使用GRUB，但却没有直接进入保护模式。在实模式下，Linux还要执行一些代码，获取一些机器状态。

Linux引导协议的文档可以在[源码](https://github.com/torvalds/linux/blob/v4.16/Documentation/x86/boot.txt)中找到。

真正的入口点位于header.S文件，符号是`_start`。首先初始化bss等section，初始化栈，执行main函数。

`boot/main.c`文件包含main函数，这是实模式下的初始化代码，主要作用就是切换到保护模式。切换之前，还要初始化console、heap、验证CPUID以保证满足系统最低要求、检测内存布局、初始化键盘、Intel SpeedStep，还有视频模式。这些步骤需要调用BIOS中断，因此必须首先在实模式下完成，将信息保存下来，再继续。

