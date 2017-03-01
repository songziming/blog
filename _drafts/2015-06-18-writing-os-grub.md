---
title: "使用 GRUB 引导自己的操作系统"
category: "底层"
tags: ["os", "grub"]
---

如果了解[计算机的启动过程](/the-starting-process-of-a-computer/)，应该会发现，计算机和操作系统启动的过程非常复杂，涉及到许多向前兼容的问题。对于操作系统，如果想利用现代硬件的新特性，就必须进行检测硬件、切换模式等一系列工作。最初，各个操作系统都自己实现引导这部分，但是引导代码涉及的底层细节很多，不同操作系统的引导代码也往往非常相似，于是就有了引导器这种专门的软件。

GRUB 是一个引导器，许多 Linux 发行版，包括 BSD 和 Solaris 都用它来引导自己的系统内核。GRUB 遵循 Multiboot 规范，符合 Multiboot 规范的内核都能由 GRUB 引导，因此让 GRUB 引导自己的内核也是很方便的。

GRUB 目前有两个版本，旧版称为 GRUB Legacy，目前最高的版本号为 0.97；新版的最高版本号是 2.0.2。本文的内容基于 Multiboot 规范的第一版，GRUB Legacy 和 GRUB 2 都支持这个版本的规范。

### Multiboot 规范

引导器的作用是引导操作系统内核，让内核开始正常的启动流程，因此引导器和内核的关系是非常紧密的。GRUB 又是一个与特定 OS 无关的软件，要做到与 OS 的紧密结合，就需要协议作为一个统一的标准。

Multiboot 是就是一个这样的规范，规定了操作系统内核镜像应该具有什么、引导器应该做什么。如果内核希望能够被引导器引导，那么内核镜像中需要包含一个数据结构，称作 Multiboot Header。这个数据结构的前 4 字节内容固定，必须位于内核镜像文件的前 4KB 之内，且总是位于 4 字节对其的位置，因此引导器可以在内核镜像中进行搜索。找到之后，就可以自从 Multiboot Header 中读出其他信息，包括内核的目标地址，长度等。

### Multiboot Header 实现

Multiboot Header 的具体要求可以参考 Multiboot Specification，这里给出 NASM 汇编实现的一个例子。

``` asm
extern  kernel_start
extern  kernel_data_end
extern  kernel_bss_end

MB1_MAGIC   equ 0x1badb002              ; magic number
MB1_FLAGS   equ 1<<0|1<<1|1<<16         ; aligned, mem info, address info
MB1_CHECK   equ -(MB1_MAGIC+MB1_FLAGS)

[section .boot]
[BITS 32]
    jmp     multiboot_entry
ALIGN 4
multiboot_header:
    dd      MB1_MAGIC
    dd      MB1_FLAGS
    dd      MB1_CHECK
    dd      multiboot_header    ; header_addr
    dd      kernel_start        ; load_addr
    dd      kernel_data_end     ; load_end_addr
    dd      kernel_bss_end      ; bss_end_addr
    dd      multiboot_entry     ; entry_addr
```

其中的 `kernel_start`、`kernel_data_end`、`kernel_bss_end` 从链接脚本中获得，指导 GRUB 将内核放在正确的位置。

### 二进制内核镜像格式

对于应用程序，可执行文件会组织城 ELF、PE 等格式。操作系统的内核通常也组织为系统默认的可执行文件格式，例如 Windows 内核为 PE 格式，Linux 内核为 ELF 格式。

Multiboot 规范对 ELF 格式进行了特别照顾，如果内核镜像是 ELF 格式的，那么引导器可以从 ELF 中读取 section 信息，将内核正确展开到制定内存地址。因此，对于 ELF 格式的内核，只需要提供 `MB1_MAGIC`、`MB1_FLAGS`、`MB1_CHECK` 这三个字段即可。

很多时候，内核更适合使用纯二进制格式，也就是没有任何多余的格式说明信息。这时就需要向 GRUB 提供内核起始地址、长度、BSS 段长度等信息。此外，如果内核是 ELF 格式的，也可以在内核中加入这些信息，这样 Multiboot Header 中的地址信息就会覆盖 ELF header 中的信息。

受限于 GRUB 的实现，引导 64 位的 ELF 镜像并不支持。这也可以通过在 Multiboot Header 中加入地址信息实现，或者直接将内核转换为纯二进制镜像。

生成纯二进制镜像可以用 objcopy 命令，但是只能通过重定位之后的 ELF 生成。
