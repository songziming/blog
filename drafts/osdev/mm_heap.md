---
title: "内存管理：堆"
---

堆可以实现任意大小对象的分配和释放，C标准库中的`malloc()`和`free()`函数，就是堆的操作接口。

Wheel中的堆是内核使用的，用户层代码会使用标准库中的实现。因此，内核堆可以相对简单，不提供动态扩容的功能。

堆将一段连续的内存划分为若干chunk，每个chunk大小不一