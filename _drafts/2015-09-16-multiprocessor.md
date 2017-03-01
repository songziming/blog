title: 编写操作系统——多处理器
category: OS Dev
tags:
- OS
- SMP
---

> 本文只关注Intel/AMD的CPU上的多核，即x86-64架构的SMP

“中断”一词有一定的歧义，本文中单指 CPU 以外产生的外部中断，如键盘、鼠标、DMA 等设备产生，最终传到 CPU 内进行处理的中断。

### 单处理器的中断控制

在介绍 SMP 下的中断之前，线回顾一下传统的 x86 CPU 是如何处理中断的。

了解过 x86 汇编应该知道，中断是处理器的一种机制，可以停下当前正在执行的指令去执行另一段指令。中断可以由 CPU 内部产生，包括内部错误如 #GP、#UD 等异常，还有使用 `int` 指令触发的软中断。此外，中断还可以来自 CPU 外部。外部中断又分为两个类别，可屏蔽中断和不可屏蔽中断（NMI，Non-Maskable Interrupt），由于是 CPU 外部产生的，需要通过 CPU 的引脚将中断信号传达 CPU，可屏蔽中断通过 INTR 引脚连到 CPU，不可屏蔽中断通过 NMI 引脚连到 CPU 上。正是因为使用不同的引脚，CPU 才能够区分它们，并使用不同的政策进行对待。

不可屏蔽中断从 NMI 接入，这种类型中断的向量号固定是 3。可屏蔽中断信号通过 INTR 引脚传入，同时向量号也通过 INTR 传到 CPU 中，因此可屏蔽中断可以具有不同的向量号。在 PC 上，可屏蔽中断和不可屏蔽中断都是通过 PIC 连到 CPU 上的，也就是鼠标键盘等外部设备首先连到 PIC，PIC 再通过 NMI 和 INTR 线连接到 CPU。设备产生了一个中断，PIC 就负责将这个中断转发给 CPU，至于转发的时候使用 NMI 还是 INTR，如果是 INTR 向量号是多少，这些属于 PIC 的配置，软件可以对 PIC 进行配置来改变这些行为。

### 多处理器的中断控制

在多处理器环境下，处理器不止一个。由于处理器变多了，系统上总共的 NMI 和 INTR 引脚的数量也会增多。PC 使用 APIC 来管理多处理器架构的中断。APIC 是一套架构，其中有一种硬件，叫做 local APIC，每个处理器都有一个自己专属的 local APIC，处理器的 NMI 和 INTR 引脚就和这个 local APIC 相连接。

这里要明确哪些功能和逻辑在处理器内部，哪些在处理器外部。中断发生之后根据向量号查 IDT，执行处理函数，这些逻辑是在 CPU 内部的，单核与多核都一样。中断从设备如何传到 CPU，这在单核与多核环境下是完全不同的。刚刚说的 local APIC 就相当于单核环境的 PIC，“包办”处理器的外来中断，处理器也不需要关心外面的世界，它之和自己 NMI、INTR 引脚所连接的设备打交道，而在多核环境下，这个设备就是 local APIC。

每个处理器都有自己的 local APIC，就像多套单核的 CPU+PIC，似乎挺不错。但 APIC 架构还规定了一种叫做 IO APIC 的设备，负责接收设备产生的中断，并将这些中断转发给各个 local APIC。IO APIC 对于每个处理器而言是共享的，但实际上处理器并不会直接访问 IO APIC。

### 向后兼容性

向后兼容是 PC 架构最令人头痛的地方。PC 体系历史悠久，并在不断发展，不断改变，但是每次改变都不会破坏已有软件的兼容性，就是因为 PC 设备有向后兼容的能力。多核出来之后，原先的单核操作系统仍然能运行。能做到这一点，是因为 PC 的 SMP 架构做了许多规定。

多核 PC 上，有一个处理器称作 Bootstrap Processor（BSP），其他的处理器都叫做 Application Processor（AP）。启动的时候，只有 BSP 启动，其他的 AP 都处在一种极低功耗的休眠状态。对于不支持多核的操作系统，系统不去检查其他处理器，不去启用它们，它们就不会运行，整个系统就像单核计算机一样，没有任何问题。当然，兼容只是保证能运行，但要想最大限度地发挥硬件的能力，还是要使用新的多核技术。因此对于一个支持多核的OS，首先要做的事情就是检测，看一下这台电脑是不是有多个处理器。如果是，初始化 APIC 和 AP。

### 中断的兼容性

前面说过，单核 PC 用 PIC 控制中断，多核计算机用 IO APIC 和 local APIC 控制中断。

- - -

现代的 CPU 很少单核了，多核已经成了标配。本文介绍了让 OS 支持多核的方式。

“多核”其实是一个不严谨的说法，正确的说法是多处理器（Multi-processor）。目前常见的多核都是对称多处理器，也就是多个 CPU 是平等的，包括他们的架构、内存访问。

### 对称多处理器

SMP 不是一个技术，而是许多中技术。SMP 需要考虑多个处理器之间的通信，从而引出一个重要的模块——APIC。APIC 分为 IO APIC 和本地 APIC 两种，本地 APIC 每个处理器核心都有一个，IO APIC 在整个系统内至少一个。本地 APIC 是对应核心的唯一中断来源，同时还可以向其他核心发送处理期间中断（IPI）。每个本地 APIC 都有一个唯一确定的 ID，由 BIOS 在系统初始化的时候指定，这些 ID 也是进行处理器间通信时使用的。

PC 发展过程中非常重视兼容性，在多处理机方面也一样。系统初始化时，其中一个核心称作引导核心（Bootstrap Processor，简称 BSP），其他的核心称作应用处理器（Application Processor，简称 AP）。BSP 负责执行引导区代码和内核，就像单处理器的机器一样，AP 停留在实模式，并处在挂起状态。除了核心，所有的本地 APIC 也有默认状态，默认状态就是 BSP 的本地 APIC 接受所有中断，所有 AP 的本地 APIC 不工作，就像单处理器机器一样。

APIC 是一种内存映射设备，也就是说，CPU 通过读写内存的方式和 APIC 交互，而不是端口 IO 操作。所有本地 APIC 的映射地址都是一样的，但每个 CPU 在访问这个地址的时候，操作的是他们各自的本地 APIC，互补干扰，因为本地 APIC 所映射的内存在不同 CPU 之间是不共享的。与此相对，IO APIC 在多个 CPU 之间是共享的，所有 CPU 访问 IO APIC 的映射地址时，访问到的是同一个 IO APIC。

### 多处理器检测

OS 想支持 SMP，首先要检测系统是否存在多个处理器。Intel 的 MP 文档详细规定了检测的方式，BIOS 在系统初始化阶段在内存中建立了两各数据结构，一个称作 MP Floating Pointer Structure，另一个称作 MP Configuration Table。MP Floating Pointer Structure 中包含了一个字段，存有 MP Configuration Table 的地址，找到 MP Configuration Table 之后，可以获取机器具有的所有 CPU 核心、总线，以及 APIC 信息，并且可以获取本地 APIC、IO APIC 在内存中的映射位置。

### 编程操作 BSP 的本地 APIC



### 参考资料

- [Multiprocessing Support for Hobby OSes Explained](http://www.osdever.net/tutorials/view/multiprocessing-support-for-hobby-oses-explained)
- [Intel MP Spec](http://developer.intel.com/design/pentium/datashts/24201606.pdf)
