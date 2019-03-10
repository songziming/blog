---
title: "物理内存管理"
---

物理内存管理器也称页帧分配器（page frame allocator），因为物理内存的分配和释放都是以页为单位的。

### 伙伴算法

Wheel使用伙伴算法（buddy algorithm）组织物理页面，将两个相邻的page按2对齐组成block，再将两个相邻的block按4对齐组成二阶block，一直到最高阶的block。

Wheel一共使用16个阶（order），也就是最高阶的块大小为128M（4K * 2^15）。每个块也按照自身大小对齐，因此两个相邻的块（互为伙伴）可以合并为高一阶的块，一个高阶的块也可以分割为两个低一阶的块。

块有两种状态：已分配和未分配。相同大小的未分配的块，相互组织成双链表，称为freelist。一共16个阶，也就是总共有16种块大小，因此总共有16个freelist。

申请物理内存时，首先计算满足需求的最小阶，并定位freelist。如果freelist为空，就继续检查更高阶的freelist。当找到一个非空的freelist，取出双链表的头元素，并将这个块不断拆分（split），直到得到一个所需大小的块，在拆分过程中产生的伙伴块则还给freelist。

释放内存的时候，则会不断检查伙伴块，如果两个块都是未分配的，那就将这两个块合并（merge），直到无法继续合并，再将合并到最大的块放回freelist。

### Zone

全部物理内存划分为三个区域（zone）：DMA、NORMAL、HIGHMEM。在AMD64架构下，DMA区域包括16MB之下的物理内存，NORMAL区域包括16MB之上的能够永久映射到虚拟地址空间中的物理内存，HIGHMEM则包含超过可映射范围的物理内存。由于AMD64的虚拟地址空间足够大，目前Wheel所支持的最大物理内存都能全部映射到虚拟空间中，因此HIGHMEM内容为空。

### 页描述符

为了保存物理页面相关的状态，Wheel定义了页描述符数据类型`page_t`：

~~~ c
typedef struct page {
    pfn_t prev;
    pfn_t next;
    u32   type : 4;
    union {
        struct {                // free
            u32 order : 4;      // only valid when block=1
            u32 block : 1;      // is it the first page in block
        };
        struct {                // pool
            u16 objects;        // first free object
            u16 inuse;          // number of allocated objects
        };
    };
} page_t;
~~~

在Linux下，类似的数据结构叫做`struct page`，Windows内核也有类似的PFN database。每个物理页面都有一个这样的描述符，组织在全局数组`page_array`中。

页描述符的`type`字段表示这个物理页面的类型，例如`PT_INVALID`、`PT_FREE`、`PT_KERNEL`等。各种类型的页面都可以通过双链表组织在一起。其余字段按照页面类型划分，使用union来节省空间。

未分配页面的类型是`PT_FREE`，按照伙伴算法，应该合并为块。块中的第一个页面`block=1`，其他的页面`block=0`。块中第一个页面的`prev`/`next`字段将各个块组织起来，形成一个freelist，代表区域中的一个order。

### 线程安全考虑

物理内存管理器是一个底层模块，系统复杂之后，很多内核代码都需要频繁申请/释放物理页面。在多核系统中，避免竞争就是一个关键问题。分配/释放页面的逻辑比较复杂，不容易设计成lockless，因此Wheel采用自旋锁保护zone。

DMA、NORMAL和HIGHMEM三个内存区域，每个区域都有自己的自旋锁。在申请/释放内存时，首先要获取这个自旋锁，操作完成之后释放。我们采用ticket-spinlock，这种自旋锁可以保证多核环境下的公平性。

对`page_array`的访问也要考虑线程安全，然而如果每个页描述符都有一个自旋锁，不但程序逻辑会非常复杂，也会浪费很多内存。然而只要程序的一致性不出现问题，就可以保证只有获得了自旋锁的线程才能访问并更新`page_array`。
