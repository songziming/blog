---
title: OS开发——中断处理
date: 2020-03-22
status: draft
---

这里不讨论CPU处理中断和异常的过程，只讨论外部硬件中断。

多核系统中，中断控制器是APIC，分为IO APIC和Local APIC，相关信息可以通过MADT获取。

涉及到中断分发的是IO APIC，定义的中断号码成为Global System Interrupt，简称GSI。对于PIC系统，外部中断只有16个，分配的中断号码是0~15，GSI可以超过16个，但是默认情况下，前面16个GSI映射到现有的PIC-IRQ。

在MADT中，可能包含interrupt override，也就是将IRQ映射到不同的GSI。我们在解析madt的时候，需要将override信息保存下来，因为我们需要键盘、PIT时钟中断的时候，唯一确定的是这些设备的IRQ号码，而不是GSI号码。因此，需要到我们的映射表中查找。

legacy ISA IRQs --> IO APIC inputs。

IO APIC中接收到的硬件中断，还不是CPU得到的中断向量好，在IO APIC这里，可以通过redirection table registers将硬件中断重定向到特定的vec num。IO APIC可以对硬件中断按照向量号排优先级。因此，最好让硬件中断的向量号尽可能稀疏。

QEMU、VirtualBox、VMWare会设置不同的IRQ->GSI映射。

## PIC

PIC是最早的中断控制器，Intel芯片组编号8259，它有8个输入，一个输出。唯一的输出会连接到CPU的INTR引脚。

每当中断发生，PIC首先通过INTR通知CPU，接下来CPU会向PIC查询IRQ编号，这样，CPU就得到了中断编号。

后来，8路中断不够用了，IBM于是将两个8259芯片级联起来，有了经典的master-slave结构。slave PIC的输出连接到master PIC的IRQ2，而slave PIC的输入IRQ0~7也被重新编号为IRQ8~15。

现在，当人们说到PIC，默认的就是级联PIC系统。后来Intel推出了升级版的8259A芯片，双PIC设计也正是进入芯片组。当时，外设总线是ISA，在当时已经够用了。由于ISA中断无法共享，人们只需要保证不同的设备使用不同的中断号就可以了。外设与中断的映射关系，也渐渐地标准化：

```
IRQ 0 — system timer
IRQ 1 — keyboard controller
IRQ 2 — cascade (interrupt from slave controller)
IRQ 3 — serial port COM2
IRQ 4 — serial port COM1
IRQ 5 — parallel port 2 and 3 or sound card
IRQ 6 — floppy controller
IRQ 7 — parallel port 1
IRQ 8 — RTC timer
IRQ 9 — ACPI
IRQ 10 — open/SCSI/NIC
IRQ 11 — open/SCSI/NIC
IRQ 12 — mouse controller
IRQ 13 — math co-processor
IRQ 14 — ATA channel 1
IRQ 15 — ATA channel 2
```

[8259A文档](https://pdos.csail.mit.edu/6.828/2005/readings/hardware/8259A.pdf)

## PCI

后来，PCI总线替代了ISA，外设的数量也突破了15。而且，ISA总线是静态的，每一种外设只能插在自己专属的插槽中，使用规定的IRQ。PCI则允许外设自由组合，好在PCI也允许多个外设共享中断。简便起见，人们直接把所有PCI设备都关联到PIRQ（Programmable Interrupt Request），让所有的PCI设备使用一个中断。

假设我们有20个PCI设备，4条PIRQ，那么可以让5个设备共用同一个PIRQ。因为当CPU收到PIRQ中断时，需要确定是哪一个PCI设备发送的，这需要轮询。减少PIRQ关联的设备数量，可以有效减少轮询次数（平衡）。

虽然只有四条PIRQ，但这毕竟要占据已有的15个IRQ。好在原有的ISA外设被PCI外设替换之后，原来的IRQ就不需要了，可以替换成PIRQ。

## APIC

PIC只能将中断发送给一个CPU，这在多核系统里就是个问题了，因此PIC也被APIC替代。这是一个全新的接口，没有兼容性要求。

每个处理器都有自己的Local APIC，同时系统还有若干全局的IO APIC，所有这些芯片通过APIC总线连接起来（在最新的系统中，使用标准的system bus）。

外设产生中断时，首先发送给IO APIC，IO APIC根据redirection table entry中的配置，将中断转发给某一个Local APIC。这样就可以实现负载均衡。

第一个APIC芯片是82489DX，内部集成了一个Local APIC和一个IO APIC。对于一个双CPU的系统，需要使用三个82489DX，一个作为IO APIC，两个作为Local APIC。可见，很大的硬件性能都被浪费了，但是好处是已有的CPU可以直接升级到APIC。后来，Local APIC被集成到了CPU内部，而IO APIC则独立出来，成为82093AA芯片。

82093AA支持24个输入，0~15留给老的ISA设备，还剩下8个可供PCI使用。82093AA最多支持16个CPU，后来升级版的xAPIC架构可以支持256个CPU，接口不变。后来，架构又升级成了x2APIC，最多支持2^32个CPU，编程方式也从MMIO改成MSR，而且x2APIC要求IOMMU。

通过CPUID，可以检查CPU支持何种APIC架构（APIC？xAPIC？x2APIC？），通过MADT，可以获取系统中IO APIC、Local APIC的全部信息，通过DSDT，可以得到中断号路由信息（哪个设备关联到哪根引脚，类似于`$PIR`）


> 参考资料：http://habrparser.blogspot.com/2019/04/external-interrupts-in-x86-system-part.html