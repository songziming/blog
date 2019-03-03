---
title: 字符终端驱动（线程安全版）
---

目前wheel已经进化成了一个多任务、多核的操作系统，但是主要的输出方式仍然是字符终端，数据竞争有时会破坏输出的内容，因此我对console模块进行了一次重构，改为lockless的实现。

### 竞争情况分析

之所以会竞争，是因为console模块具有很多全局变量，光标所在的行号/列号、字符颜色等，这些变量是共享的，所有需要打印输出的代码都会使用并更新这些变量。

为了避免竞争，最直观的想法就是加锁。自旋锁可以防止不同CPU之间的抢占，关闭中断可以防止任务切换与ISR的抢占。然而，异常处理程序的抢占却是无法屏蔽的，而异常处理函数同样需要打印输出。总结起来，可能引发数据竞争的有这些情况：

- 多核。不同CPU上执行的代码有可能同时使用终端打印函数`console_puts()`。
- 任务切换。切换之前的任务可能正在执行`console_puts()`函数，但是在目前的实时调度策略下，这种情况应该不会出现。
- 中断。若在任务执行`console_puts()`时发生了中断，而中断处理函数中又调用了`console_puts()`，就会发生竞争。
- 异常。类似于中断的情况，而且无法通过`cli`屏蔽。

VxWorks的做法是，禁止中断和异常处理函数使用`printf()`这类的阻塞性输出函数，并提供了`logMsg()`，用于缓存输出的内容并由专门的任务`tLogTask`打印。wheel没有采取这个方法，而是修改了console驱动，使其成为线程安全的（thread-safe），这样即使多个硬件线程同时调用`console_puts()`，也不会产生冲突。

### lockless算法

虽然主要用到的是`console_puts()`，但无锁的函数是`console_putc()`，它负责输出单个的字符。输出字符的同时，还要调整光标位置`caret_row`和`caret_col`，还可能更新颜色属性`text_attr`。如果光标的超过了列边界，需要换到下一行；如果超过了屏幕的范围，还需要滚屏，涉及到内存拷贝`memcpy`。

我们设计的这套无所算法，将所有全局变量整合为一个变量：

~~~ c
typedef struct console_loc {
    u8 caret_row;
    u8 caret_col;
    u8 text_attr;
    u8 start_row;
} __PACKED console_loc_t;

static console_loc_t loc;
~~~

这样的结构体，存储空间正好是一个`u32`，因此可以使用一条原子性操作进行更新。和原来相比，多了一个`start_row`字段，表示起始行号，也就是显示出来的第一行对应缓冲区中的行编号。

无锁版本的`console_putc()`基本逻辑如下：

~~~ c
void console_putc(char c) {
    u32 old, new;

retry:
    old = atomic_get(&loc);
    new = update_caret_position(old);

    if (!atomic_cmp_and_set(&loc, old, new)) {
        goto retry;
    }

    // copy char to old location
}
~~~

这里采用了一个cas-loop模式，是一种常见的无锁设计模式。首先获取原来的console状态，计算出新的状态但不更新。更新操作是通过一个compare-and-set原子操作完成的。如果这一步原子操作失败，说明全局变量`loc`的值在这段时间内发生了变更（可能是其他CPU上的代码修改的），需要重新执行更新操作。如果原子操作成功，说明我们成功预留了一个位置，接下来只需要将字符`c`复制到那个位置即可。

### 完整版`console_putc`代码

~~~ c
#define ROW_COUNT       25
#define COL_COUNT       80
#define POS(row, col) ((((row) + ROW_COUNT) % ROW_COUNT) * COL_COUNT + (col))

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
        u64 * line = (u64 *) &vbuf[POS(next->base, 0)];
        next->base += 1;
        for (int j = 0; j < COL_COUNT / 4; ++j) { line[j] = fill; }
    }

    if (!atomic32_cmp_and_set((u32 *) &location, old_val, new_val)) {
        goto retry;
    }

    if (prev->base != next->base) {
        for (int i = 0; i < ROW_COUNT; ++i) {
            memcpy(&vram[POS(i, 0)], &vbuf[POS(next->base + i, 0)], 2 * COL_COUNT);
        }
    }

    if ('\t' != c && '\n' != c && '\r' != c) {
        u16 fill = (u16) c | ((u16) prev->attr << 8);
        vbuf[POS(prev->row, prev->col)] = fill;
        vram[POS(prev->row - next->base, prev->col)] = fill;
    }
}
~~~

这里需要说明，`vram`是显存的地址，`vbuf`则是内存中的一段缓冲区。每次输出字符的时候，首先将数据写入`vbuf`再复制到`vram`。在滚屏时，可以直接将`vbuf`的内容增加一行的偏移复制到`vram`，避免读取显存的内容（读取显存速度很慢）。

`row`和`col`指的都是`vbuf`里面的行/列编号，其中`row`有可能超过总行数的限制，因此每次访问`vbuf`的时候，都要通过宏`COORD`限制在边界检内。
