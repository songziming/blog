title: 编写操作系统——环境工具
category: OS Dev
tags:
- OS
---

本文介绍的系统叫做 Wheel，可以在[这里](https://github.com/songziming/wheel)看到它的源代码。编写这个系统的目的并不是创造另一个 Linux 或 Windows，而是学习操作系统的原理以及 PC 硬件组成，这也是我将其命名为“轮子”的原因。目前，Wheel 只能运行在 Intel 和 AMD 的 64 位 CPU 之上，且只能在 64 位模式下工作。由于这是一个全新的系统，没有任何兼容性要求，因此在 Wheel 中可以大胆地使用很多硬件的新特性。

这篇文章介绍开发的环境、工具，和构建系统。

### 开发环境和工具

Wheel 在 64 位 Linux 下开发，这是因为 Linux 系统的开发工具非常丰富。

Wheel 主要使用 C 语言编写，但由于操作系统需要与底层交互，汇编也是不可避免的。因此两个必须的工具是 C 语言编译器和汇编器，Wheel 分别采用 Clang 和 Yasm。Clang 是 LLVM 的 C 编译器，发展势头很好，而且据称生成的代码比 GCC 质量更高；Yasm 是一个基于 Nasm 的汇编器，使用 Intel 语法，并且提供了 64 位汇编的能力。

链接器采用 GNU-ld，构建工具采用 GNU-Make，链接脚本和 Makefile 后面会介绍。引导器使用 GRUB（0.97版，高版本的同样可以），测试操作系统使用 QEMU 虚拟机，通过虚拟软盘引导。

将操作系统内核写入软盘镜像，可以在 Linux 下挂载镜像到一个目录，并使用文件操作写入内核，但这样需要 root 权限，集成到 Makefile 中不方便，因此，Wheel 采用 MTools 工具实现将内核写入软盘镜像。MTools 可以操作 MS-DOS 磁盘镜像，而且不需要挂载。

### 引导器 GRUB

有的开发者习惯自己编写引导器，以加深对系统的理解。但是，PC 平台的历史包袱很重，每个新功能的加入都需要保证和旧版本兼容。向后兼容的结果就是很多硬件的新特性都需要软件去启用才能生效，在操作系统引导阶段，需要进行一系列初始化和模式切换工作，包括从启动介质读取内核载入内存，开启 A20，进入保护模式。使用一个现有的引导器，可以跳过这些繁琐的步骤。

GRUB 是一个优秀的引导器，支持 Multiboot 规范，只要内核镜像遵循 Multiboot 规范，就能够被 GRUB 引导。而且，GRUB 能够识别文件系统，安装内核到启动介质只需要进行文件复制就可以，不需要进行绝对扇区写入。

### 链接脚本

链接是指将编译生成的可重定位目标文件组合成单一的可执行文件的过程。对于一般的应用程序，其内存布局由操作系统进行管理，但是对于内核，必须明确知道自己在内存中的分布情况。GNU-ld 提供了链接脚本的功能，允许开发者规定可执行文件的内存布局。Wheel 使用的链接脚本如下：

``` ld
OUTPUT_FORMAT(binary)
SECTIONS {
    /DISCARD/ : {
        *(.comment)
        *(.note.GNU-stack)
        *(.eh_frame)
    }
    . = 0x100000;
    kernel_start = .;
    .text : {
        kernel_text_start = .;
        *(.boot)
        *(.text*)
        kernel_text_end = .;
    } = 0x90    /* NOP */
    .data : {
        kernel_data_start = .;
        *(.rodata*)
        *(.data*)
        kernel_data_end = .;
    } = 0
    .bss : {
        kernel_bss_start = .;
        *(COMMON)
        *(.bss)
        kernel_bss_end = .;
    } = 0
    kernel_end = .;
}
```

这个脚本规定了各个 section 在内存中的布局，其中 `boot` 包含 GRUB 需要的信息，因此放在首位。每个 section 都有符号记录起始位置，这些位置在 Multiboot 头中使用。

### Makefile

操作系统的源代码通常很大，文件很多，编译链接的步骤也很复杂。因此，最好使用 GNU-Make 来将这个过程自动化。GNU-Make 并不是唯一的自动化构建工具，但是它的功能最基础，最底层，这对于开发操作系统来说恰恰是最重要的，因为底层就意味着更充分地掌控。

下面是 Wheel 使用的 Makefile：

``` Makefile
# directories
inc_dir :=  include
src_dir :=  kernel
dst_dir :=  build

# files
sources :=  $(foreach dir, $(src_dir), $(shell find $(dir) -name '*.asm' -o -name '*.c'))
headers :=  $(foreach dir, $(src_dir) $(inc_dir), $(shell find $(dir) -name '*.h'))
objects :=  $(foreach obj, $(patsubst %.asm, %.asm.o, $(patsubst %.c, %.c.o, $(sources))), $(dst_dir)/$(obj))

bin     :=  $(dst_dir)/kernel.bin
map     :=  $(dst_dir)/kernel.map
lds     :=  link.lds
fda     :=  fd.img

# toolchain
AS      :=  yasm
ASFLAGS :=  -f elf64
CC      :=  clang
CFLAGS  :=  -c -std=c11 -O2 -Wall -Wextra -I $(inc_dir) \
            -ffreestanding -fno-builtin -nostdinc -nostdlib \
            -fno-stack-protector -fno-zero-initialized-in-bss -fno-sanitize=address \
            -mcmodel=large -mno-red-zone -mno-mmx -mno-sse -mno-sse2 -mno-sse3 -mno-3dnow
LD      :=  ld
LDFLAGS :=  -nostdlib -z max-page-size=0x1000

# pseudo-targets
.PHONY: all kernel write run clean

all: kernel write run

kernel: $(bin)

write: $(bin) $(fda)
	@echo "\033[1;34mwriting to floppy image\033[0m"
	@mcopy -o $(bin) -i $(fda) ::/

run: $(fda)
	@echo "\033[1;31mexecuting qemu\033[0m"
	@qemu-system-x86_64 -m 32 -smp 2 -fda $(fda)

clean:
	@echo "\033[1;34mcleaning objects\033[0m"
	@rm $(objects) $(bin)

$(bin): $(objects) $(lds)
	@echo "\033[1;34mlinking kernel\033[0m"
	@mkdir -p $(@D)
	@$(LD) $(LDFLAGS) -T $(lds) -Map $(map) -o $@ $^

$(dst_dir)/%.asm.o: %.asm
	@echo "\033[1;32massembling $< to $@\033[0m"
	@mkdir -p $(@D)
	@$(AS) $(ASFLAGS) -o $@ $<

$(dst_dir)/%.c.o: %.c $(headers)
	@echo "\033[1;32mcompiling $< to $@\033[0m"
	@mkdir -p $(@D)
	@$(CC) $(CFLAGS) -o $@ $<
```

上面的 Makefile 将编译链接生成的文件放在 `build` 目录下，保证源代码目录树的干净。并且使用通配符来匹配 C 语言和汇编的编译规则。链接阶段，除了生成内核镜像，还创建了一个 map 文件，这个文件中包含了内核镜像中所有符号所在的内存地址，在调试的时候非常有用。

### 参考资料

世界上有许多人开发自己的操作系统，志同道合的人还是有的，下面是两个比较大的社区：

- [OSDev](http://wiki.osdev.org/Main_Page)
- [OS Development Tutorials](http://www.osdever.net/tutorials/)

然而，社区的信息大多是编写 32 位保护模式操作系统的，对于 64 位长方式、多核等新技术的资料相对较少，这是就需要参考 AMD、Intel 提供的文档了。
