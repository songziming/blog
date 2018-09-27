---
title: "无锁算法"
---

本文是阅读[1024cores](http://www.1024cores.net/home/lock-free-algorithms)的笔记。

论文[Wait-free synchronization](https://dl.acm.org/citation.cfm?doid=114005.102808)。

Intel关于原子性操作的[建议](https://software.intel.com/en-us/articles/implementing-scalable-atomic-locks-for-multi-core-intel-em64t-and-ia32-architectures)。

在讨论wait-free算法时，说到的thread（线程）通常指硬件线程，也就是能够真正同时执行的指令流。但是这个线程推广到软线程，结论依然适用。

### lock-free v.s. wait-free

这里有两个类似的概念：lock-free和wait-free。wait-free的意思是，不管外部环境如何，每个线程都可以一直保持运行，不会阻塞等待。每一个操作都可以在有限步骤内完成。这是对同步算法最强有力的保证。lock-free的意思是，不管外部环境如何，当前线程都可以移植保持运行。可以看出，lock-free只关心当前线程，至于其他的线程是否发生了阻塞，我们并不关心。因此，lock-free比wait-free的约束更少，为了实现更高的总体性能，我们要追求的应该是wait-free，即无等待算法。

如果一个算法使用了cas-loop，那么这个算法应该属于lock-free，但不属于wait-free，因为单个的线程有可能因为cas失败而循环，但是整体来看，不会导致所有的线程的阻塞，整体系统还是在正向执行的。

还有另外一个概念：obstruction-free（无障碍），这个概念是说，当一个线程与其他的线程之间没有竞争的时候，这个线程保证能够正向执行。这是比lock-free还要宽松的约束。

为了实现无锁算法，我们通常会使用一些原子性操作，例如atomic_add、atomic_inc，但是很少使用atomic_cas，因为cas-loop带有循环，这种不断检查直到成功的做法本身不能保证原子性。

如果硬件提供了 fetch_and_add 操作，那我们就要避免使用 cas-loop，因为 fetch_and_add 没有循环的需要，能够在有限时间内完成操作，而 cas-loop 不能对执行的时间给出一个确定性的上限。而且 cas 对缓存的影响也比 xadd 更加严重。而且 cas 还涉及到了分支预测。总之，用 xadd，避免 cas。

起码就x86架构而言，提供了xadd指令，但没有提供能够实现 fetch_and_or 这类原子位运算的指令。虽然说借助 cas-loop 可以实现所有的原子操作，但这种模式已经证明不可靠，因此wheel的代码里应该尽量避免使用atomic_and。不要使用GCC内置的sync实现，因为这些操作很有可能也使用 cas-loop 实现的。

可以使用的：atomic_add、atomic_sub、atomic_inc、atomic_dec、atomic_cas。

### 评价指标

衡量一个wait-free算法的好坏，要看一个操作会导致多少缓存通信。多个Core同时操作一个缓存，CPU为了保持缓存一致性，就要在多个缓存行之间进行同步，这是会降低性能的，因此一个操作导致的缓存通信越少，我们就认为这个操作越高效。

我们希望一个并行算法是线性加速比的，也就是整体运行效率正比于线程数，这是一个相当理想的情况，实际很难实现，但我们的目的就是尽量接近。

内存读取操作是线性加速的（scales linearly），写操作会导致缓存通信，