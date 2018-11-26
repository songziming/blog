处理器间中断。

多核环境下，可以使用Local APIC发送中断到其他CPU，实现跨处理器的消息。Local APIC同时也是中断控制器，替代8259 PIC。不同之处是，Local APIC除了可以接收中断，还可以发送中断。

处理器间中断简称IPI（Inter-Processor Interrupt），实际上，启动SMP的时候，就已经使用到了IPI，只不过当时使用的是INIT和SIPI这两种特殊类型。

发送IPI的步骤很简单，向Local APIC映射在内存中的ICR（Interrupt Command Register）寄存器写入值即可。

### ICR - Interrupt Command Register

ICR总共64位，分割成两个32位寄存器，映射到0x300和0x310两处。向ICR写入值的时候，应该首先写入高32位，再写入低32位，因为只有0x300处发生写操作时，才会触发Local APIC发送IPI。

高32位映射在0x310，内容非常简单，最高8bit包含目标CPU的apic ID。

低32位映射在0x300，内容相对复杂一些：
- 首先是8bit中断向量号，表示目标CPU接收到这个IPI时，向量号的取值。
- 接下来两个bit表示目标模式，0表示正常
- 目标类型，0表示使用高32bit中指定的ID
- 只读位，表示这个中断的状态
- 保留
- Clear for INIT level de-assert, otherwise set.
- Set for INIT level de-assert, otherwise clear.
- 两个bit，Destination type. If this is > 0 then the destination field in 0x310 is ignored. 1 will always send the interrupt to itself, 2 will send it to all processors, and 3 will send it to all processors aside from the current one. It is best to avoid using modes 1, 2 and 3, and stick with 0.
- 剩余位保留

### IPI传递参数

通过ICR可以向其他处理器发送中断，然而却不能传递参数