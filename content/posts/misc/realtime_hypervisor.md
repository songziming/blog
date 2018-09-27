---
title: "实时虚拟化"
---

要做一个虚拟化平台，满足实时性，支持多核。

支持多核的RTOS，本身就是一个不小的项目。关于多核硬件上的实时调度算法，有不少的研究。

实时应用软件运行在RTOS上才有保证，而RTOS都是在真实硬件上测试并验证的。也就是说，运行在真实硬件上的RTOS才有保证。

RTOS保证虚拟化的前提：
- 按优先级关系进行确定性调度，去掉调度过程中的不可预测性
- 当一个硬件中断到来时，用最短（并且有上限）的时间执行注册的ISR，并用最短时间恢复某个pending状态的任务

如果我们要让hypervisor支持虚拟化，有两种策略：

- 保证当中断到来的时候，可以迅速执行指定的VCPU
- 基于一个RTOS，让RTOS处于idle状态时执行非实时的任务
- 在多核平台上，对处理器进行分区，

第二种方法更容易，相当于融合了VM与local threading，我们完全可以拿来一个实时OS，然后在上面把idle task给换成另一套调度算法。但是这样的话，实时核分时的任务处在不同的层次中

### Case Study：NI realtime hypervisor

> The NI LabVIEW Real-Time Module is a solution for creating reliable, stand-alone embedded systems with a graphical programming approach.

虽然