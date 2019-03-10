---
title: 字符终端驱动（无锁实现）
---

在多核硬件上，每个硬件线程都有打印输出的需求，这就要求字符终端驱动是线程安全的（thread-safe）。本文介绍一种无锁（lockless）字符终端的实现，该方法只需要一些原子性操作函数，对系统没有其他的要求。

### 原子性操作

无锁算法的关键是各种原子性操作。本文涉及到的原子性操作包括：

- `atomic32_get(u32 * var)`，获取原子变量`*var`的取值。
- `atomic32_cas(u32 * var, u32 old, u32 new)`，比较原子变量`*var`与`old`的取值，如果相等，那么将`*var`置为`new`，反之不进行任何操作，最后返回`*var`的原值。

### 竞争情况分析

字符终端模块的核心接口是`console_putc()`，用于打印一个字符到终端，同时处理换行、滚屏等操作，更新光标位置。由于只有一个字符终端设备，console模块使用全局变量来存储光标位置、当前字符颜色等信息。正是全局变量的存在，导致多线程环境下会发生数据竞争。

为了避免竞争，最直观的想法就是加锁。自旋锁可以防止不同CPU之间的抢占，关闭中断可以防止任务切换与ISR的抢占。然而，异常处理程序的抢占却是无法屏蔽的，而异常处理函数同样需要打印输出。总结起来，可能引发数据竞争的有这些情况：

- 多核。不同CPU上执行的代码有可能同时使用终端打印函数`console_puts()`。
- 任务切换。切换之前的任务可能正在执行`console_puts()`函数，但是在目前的实时调度策略下，这种情况应该不会出现。
- 中断。若在任务执行`console_puts()`时发生了中断，而中断处理函数中又调用了`console_puts()`，就会发生竞争。
- 异常。类似于中断的情况，而且无法通过`cli`屏蔽。

VxWorks的做法是，禁止中断和异常处理函数使用`printf()`这类的阻塞性输出函数，并提供了`logMsg()`函数，用于将输出的内容发送给专门的任务`tLogTask`。wheel没有采取这个方法，而是修改了console驱动，使其成为线程安全的（thread-safe），这样即使多个硬件线程同时调用`console_puts()`，也不会产生冲突。

### 无锁算法

一个典型的无锁算法设计被称作“CAS-loop”，伪代码如下：

~~~ c
retry:
    old = atomic32_get(&var);
    // do something about `old`
    // about to change it to `new`
    if (atomic32_cas(&var, old, new) != old) {
        goto retry;
    }
~~~

按照正常的算法流程，我们需要将变量`var`的值由`old`更新为`new`。然而在计算`new`的过程中，其他线程可能修改了`var`的值，导致根据`old`计算出来的`new`不再有意义。为此，将更新的赋值操作替换为CAS（compare-and-set），这个操作只有在`var==old`时才会执行赋值，而`var==old`表示之前的计算过程没有发生竞争，计算出来的`new`是有意义的。

如果`var`的取值不是`old`，说明在之前的计算过程中，其他线程修改了`var`，那么之前的计算过程需要重复进行一遍。

### 无锁字符终端

console模块有很多个全局变量，然而“CAS-loop”只能有一个原子变量。因此我们需要将console的状态压缩为一个`u32`类型：

~~~ c
typedef struct {
    u8 row;     // current caret row index
    u8 col;     // current caret column index
    u8 attr;    // current text attribute
    u8 base;    // row number of starting line
} __PACKED loc_t;

static loc_t location;
~~~

字符界面共有80列，25行，每个单元占2字节，映射在显存`vram`处，同时RAM中还有相同大小的一段缓冲区`vbuf`。每次输出字符，首先写入`vbuf`，再复制到`vram`。

`vbuf`是线性写入的，但`vram`需要处理滚屏。`base`字段就表示`vbuf`与`vram`的行偏移。

### 完整代码

以下是完整的`_console_putc()`函数代码。

~~~ c
#define ROW_COUNT       25
#define COL_COUNT       80
#define IDX(row, col) ((((row) + ROW_COUNT) % ROW_COUNT) * COL_COUNT + (col))

static void _console_putc(char c) {
    u32     old_val;
    u32     new_val;
    loc_t * prev;
    loc_t * next;

retry:
    old_val = atomic32_get((u32 *) &location);
    new_val = old_val;
    prev    = (loc_t *) &old_val;
    next    = (loc_t *) &new_val;

    switch (c) {
    case '\t': next->col += 8; next->col &= ~7; break;
    case '\n': next->col  = 0; next->row +=  1; break;
    case '\r': next->col  = 0; break;
    default:   next->col += 1; break;
    }

    while (next->col >= COL_COUNT) {
        next->col -= COL_COUNT;
        next->row += 1;
    }

    u64 fill = (u64) ' ' | ((u64) prev->attr << 8);
    fill |= fill << 16;
    fill |= fill << 32;
    while (next->row - next->base >= ROW_COUNT) {
        u64 * line = (u64 *) &vbuf[IDX(next->base, 0)];
        next->base += 1;
        for (int j = 0; j < COL_COUNT / 4; ++j) { line[j] = fill; }
    }

    if (atomic32_cas((u32 *) &location, old_val, new_val) != old_val) {
        goto retry;
    }

    if (prev->base != next->base) {
        for (int i = 0; i < ROW_COUNT; ++i) {
            memcpy(&vram[IDX(i, 0)], &vbuf[IDX(next->base + i, 0)], 2 * COL_COUNT);
        }
    }

    if ('\t' != c && '\n' != c && '\r' != c) {
        u16 fill = (u16) c | ((u16) prev->attr << 8);
        vbuf[IDX(prev->row, prev->col)] = fill;
        vram[IDX(prev->row - next->base, prev->col)] = fill;
    }
}
~~~
