---
title: "内存管理：内存池"
---

内存池将内存页进一步划分，拆分成若干的object，并组织成一张链表。为了支持内存池，`page_array`中需要增加以下两个字段：

- `inuse`，表示这个页面内，有多少object是已分配的状态。
- `objects`，表示在这个页面内，第一个空闲状态的object的偏移。

`page_t`的大小非常关键，为了节省内存，应该尽量紧凑

objects不可能超过页的大小，因此objects的取值一定小于`PAGE_SIZE`，也就是最多占用`PAGE_SHIFT`个比特。此外，我们还应该考虑到object的对齐要求。对于空闲状态的object，我们需要用它的空间保存next指针，而这个next指针是u32类型的，也就是占用4字节，因此object必然是4字节对齐的，因此objects字段最多占用`PAGE_SHIFT-2`个比特。

以x64为例，PAGE_SHIFT为12，如果我们希望objects最多占用8bit，也就是说所有的object都必须是64字节对其的（2^16）。

inuse字段类似，占用的空间与objects相同。

如果希望page_t更紧凑，是否可以完全使用u32类型，划分为不同的field，根据不同的用途使用不同bit：
- 3bit表示page类型
- 1bit表示这个page是否属于某个block，如果是，表示这个page不是block的头元素，因此prev、next无意义
- 4bit表示block order，这4bit只对block头元素有效。最大order=15，也就是 4K*2^15 = 32MB，如果我们限制最大order为14，也就是16MB，感觉上也是够用的。