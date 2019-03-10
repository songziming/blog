---
title: 物理页面管理
---

物理内存管理是一切内存管理的基础，有了物理内存之后，才能讨论堆和内存池。

物理内存分为固定大小的页（page），物理内存的分配/回收也是以页为单位进行的。

### Page Array

为了方便管理，操作系统需要为每个物理页面创建一个`page_t`对象，通常组成一个大数组，在系统启动阶段分配和初始化。在Wheel中，`page_t`的结构是这样的：

~~~ c
typedef struct page {
    pfn_t prev;
    pfn_t next;
    u16   type  : 4;        // page type
    u16   order : 4;        // the order of this block
    union {
        struct {            // slab
            u16 inuse   : PAGE_SHIFT;
            u16 objects : PAGE_SHIFT;
        };
        struct {            // mmu page table, can be shared
            u32 ref_count;
        };
        // TODO: add more type
    };
} __ALIGNED(sizeof(usize)) page_t;
~~~

在很多操作系统中都可以看到类似的设计，例如Linux中的`struct page`，Windows内核中的`PFN database`。Wheel将`page_t`设计的尽量紧凑，以节省更多内存。

### 伙伴算法

Wheel采用伙伴（buddy）算法管理物理页面。