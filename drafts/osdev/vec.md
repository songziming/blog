中断向量号分配。

PC硬件的历史负担比较重，因此PIC、APIC这种功能重合的控制器都存在。尤其是APIC，向量号的分配还会影响到中断的优先级。

可以参考一下Linux是如何分配向量号的：

- 0~0x13，CPU内部异常和NMI
- 0x14~0x1f，Intel保留
- 0x20~0x7f，外部中断（包括IO APIC中配置的redirect entries，以及传统PIC的保留向量号）
- 0x80，系统调用
- 0x81~0xee，外部中断
- 0xef --> local apic timer interrupt
- 0xf0 --> local apic thermal interrupt
- 0xf1~0xfa --> reserved for future use
- 0xfb~0xfd --> interprocessor interrupts
- 0xfe --> local apic error interrupt
- 0xff --> local apic spurious interrupt

可以看出，前面一部分是Intel规定的，Linux无法改变。local apic的几个中断，向量号对优先级影响不大，因此安排在中断空间的最后，包括IPI，也挤在这一块。剩下的空间，全部分配给外部硬件中断，除了中间0x80插进来一个系统调用。

Linux 支持三种IPI，分别用来：
1. 通知另一个CPU执行reschedule函数
2. 通知另一个CPU清空TLB的内容
3. 通知另一个CPU执行一个函数，该函数通过一个全局变量`call_data`传递

如果这样分析，前面两种IPI同样可以使用第三种机制实现，区别在于，如果我们将一些常见的IPI单独分配向量号，这个向量号的IPI就可以不需要call_data，让IPI执行过程更高效。

### 调度过程中的IPI

多核调度器是IPI使用的常见情况，如果一段代码创建了新的task，然而新的task通过affinity指定需要在另一个CPU上面运行，这时就需要执行IPI。

wheel的调度器使用tid_prev和tid_next两个核心变量，分别表示当前正在执行的任务，以及接下来要执行的任务。tid_next并不是随便就可以修改的，必须在取得了目标CPU的就绪队列自旋锁的时候修改。

如果释放一个新的任务，要在另一个CPU上执行，我们会获取另一个CPU的readyq自旋锁，并修改另一个CPU的tid_next。也就是说，操作就绪队列、赋值tid_next这些操作不一定要在当前CPU上完成，其他CPU可以“代劳”，毕竟有自旋锁保护。
但关键问题是，我们帮另一个CPU修改了tid_next，被帮忙的CPU未必知道，因此需要发送一个IPI。这个IPI不需要做任何事，只需要走一遍int_entry以及int_return即可，因为在中断返回的过程中，会加载tid_next的上下文，实现任务切换。