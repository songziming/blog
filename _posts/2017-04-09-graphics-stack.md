---
title: "Graphics Stack"
category: "开发"
published: false
---

Graphics stack is a layered approach to GUI, analogous to the networking stack. A general model for a graphics stack looks like this:

- Application Layer
- Interoperation Layers
    - Desktop Management Layer
    - Window Management Layer
- Presentation Layers
    - Compositing Layer
    - Widget Toolkit Layer
    - Rendering Layer
- Display Layers
    - Device Driver Layer
    - Hardware Layer

### Device Driver Layer

This layer of software communicate with the actual hardware - the video memory, the GPU (if any), the video signal generator, and even the monitor.

VESA VBE/Core定义了和显示硬件交互的最小接口。OS需要首先通过BIOS接口获取VESA的信息。但是BIOS调用只能在实模式下使用，不过GRUB所遵循的Multiboot规范考虑到了这一点，可以通过MultibootInfo获取VBE信息。

仅仅获取信息还不够，OS还需要设置图形显示模式。toaruOS是一个支持GUI的OS，切换图形模式的办法也很简单——通过GRUB：

```
/* Multiboot section */
.long MB_MAGIC
.long MB_FLAGS
.long MB_CHECKSUM
.long 0x00000000 /* header_addr */
.long 0x00000000 /* load_addr */
.long 0x00000000 /* load_end_addr */
.long 0x00000000 /* bss_end_addr */
.long 0x00000000 /* entry_addr */

/* Request linear graphics mode */
.long 0x00000000
.long 0
.long 0
.long 32
```

指定显示器为图形模式，长宽不指定，由GRUB设置，颜色深度为32位。不指定预期的长宽尺寸，意味着让GRUB自己选择合适的分辨率设置，这也是应该的，至于VirtualBox/VMWare这类虚拟机的屏幕尺寸切换功能，自然有专门的协议。

### GUI for OS

能给自己的OS添加图形界面当然是很有趣的事情，然而写一个GUI并不简单。不想OS的其他方面，GUI需要和显示设备打交道，而各个显示设备（显卡）的操作方式又各不相同，没有统一的API。不过，我们暂时不需要考虑3D显示、硬件加速这类高级话题。

VGA是一种比较普遍的显示设备，当今大部分显卡都可以认为兼容VGA模式。但是VGA模式对显示分辨率有限制，最高只能到640x480。VGA将原来的若干芯片整合为单一的芯片，内部包括：
- Video Buffer，显存，通过MMIO映射到内存地址空间。
- Video DAC
- CRT Controller
- Sequencer
- Graphics Controller

标准VGA的显存映射地址范围是`0x000A0000-0x000BFFFF`，共计640K。但是，不同显示模式下显存的映射位置不同。

### SVGA

VGA标准可以让OS使用统一的方法来操作显示设备，但是分辨率低，且缺乏硬件加速功能。

VBE表示Vesa BIOS Extensions，可以用来操作SuperVGA设备。

VBE模式号，一个十六位无符号数，从QEMU模拟来看，QEMU上支持的显示模式只有bank switching mode，并不支持Linear Frame Buffer，这稍稍有些可惜。
