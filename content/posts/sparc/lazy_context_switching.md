---
title: "SPARC 任务切换优化"
# kind: "article"
tags: ["os"]
---

在 SPARC 架构下，切换任务时需要把所有寄存器的内容保存到栈上（flush window），确保任何一个时刻，所有寄存器窗中不会同时存在多个任务的数据。

然而，flush window 需要执行较多的内存写操作，最好能够在数据发生冲突的时候再执行保存操作。

### 常规任务切换过程

通常 `%wim` 将一个比特置为 1，也就是只有一个寄存器窗被标记为无效。`%cwp` 是当前正在使用的窗口的编号，`%cwp` 到 `%wim-1` 之间所有窗都包含数据，因此当一个任务即将换出的时候，我们需要把这些寄存器窗里的内容保存到栈上，同时还包括最后一个栈的 outs 寄存器。

当所有重要的寄存器都保存到栈上之后，寄存器窗的状态应该是这样的，`1 << (%cwp + 1) == %wim`：

![figure of regwin status]()

