---
title: "内存管理：物理页"
---

物理内存管理是一切内存管理的基础，有了物理内存之后，才能讨论内存池和堆。

物理内存管理，也就是对物理页面的分配和释放。通常，申请到一个物理页面之后，还需要操作MMU，将新分配的物理页面映射到虚拟地址空间中，但这并不是物理内存管理器的任务。

### Page Array

Wheel系统在启动阶段探测内存，获得物理内存的大小和布局信息，并创建`page_array`数组。这是一个`page_t`对象构成的数组，每个元素描述一个物理页面。`page_t`类型的定义如下：

~~~ c
typedef struct page {
    pfn_t prev;
    pfn_t next;
    u8    type;             // page type
    u8    order;            // the order of this block
    union {
        struct {            // slab (what if PAGE_SHIFT is larger than 12?)
            u16 inuse   : PAGE_SHIFT;
            u16 objects : PAGE_SHIFT;
        };
        struct {            // mmu page table, can be shared
            u32 ref_count;
        };
    };
} __ALIGNED(sizeof(usize)) page_t;
~~~

### 伙伴算法

伙伴（buddy）算法将物理页面组织成块（block），每个块都包含数量为2的幂的连续物理页面，并且起始地址也是按照数量对齐的。

### 如何寻找一个page所属的block

如果`page_array[i].order == NO_ORDER`，表示这个页面属于某个block，且不是block中的第一个页面。

如果想快速找到一个block的开头页面，可以按2的幂不断二分搜索（向前）。具体的做法，就是不断将当前页号的最后一个bit清零，这样就相当于不断向前搜索，而且效率很高，自动跳过block中间的page。至于去掉最后一个bit的方法，也很直接：`(a & (a-1))`。