---
title: "物理内存管理"
# kind: "article"
tags: ["memory", "os"]
---

物理内存管理负责分配和释放物理内存，这是 malloc/free 这些虚拟内存管理机制的基础。物理内存管理有许多种机制，这篇文章描述 [Wheel](https://github.com/songziming/wheel) 中使用的算法。

Wheel 大体上参考了 Linux 的 buddy allocator，将物理内存按 2 的幂组织成不同级别的 block，分配内存的时候，会将较大的 block 分割，回收内存的时候，会与相邻同级别的空闲 block 合并，形成一个更大的 block。但是与 Linux 不同的是，我们并没有使用位图来表述各个 block 的状态，而且能够不按照 block 的边界分配/释放内存。