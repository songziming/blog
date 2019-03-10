---
title: "Wheel构建系统"
---

Wheel使用GNU Make来指导整体的构建流程。

普通的应用程序构建流程相对简单：将每一个源文件编译为目标文件、将所有的目标文件和库文件链接为一个可执行文件。而操作系统除了需要生成内核镜像，还需要编译若干用户层应用程序，并将相关资源文件打包，生成可引导的磁盘镜像。只有得到一个可引导镜像，才能通过虚拟机运行，或者烧写到存储器并从真机上运行。

### 交叉编译器

编译操作系统应该使用交叉编译器，即使开发机和目标架构相同。目前Wheel支持AMD64架构，因此应该使用目标为`x86_64-elf`的GCC交叉编译器。

构建交叉编译器的过程可以参考OSDev上的文章[GCC Cross-Compiler](https://wiki.osdev.org/GCC_Cross-Compiler)，编译过程的命令如下：

~~~ bash
# build binutils
mkdir build-binutils && cd build-binutils
../binutils-x.y.z/configure --target=x86_64-elf --with-sysroot --disable-nls --disable-werror
make -j4
sudo make install

# build gcc
mkdir build-gcc && cd build-gcc
../gcc-x.y.z/configure --target=x86_64-elf --disable-nls --enable-languages=c,c++ --without-headers
make all-gcc -j4
make all-target-libgcc -j4
sudo make install-gcc
sudo make install-target-libgcc
~~~

### 用户层与内核层

Wheel的构建过程分为user和kernel两个阶段，即构建用户层应用和内核镜像。两个过程相对独立，但某些用户层应用可以打包为RAMFS，内嵌在内核镜像中，这也是首先构建user的原因。

### 架构相关层

此外，Wheel还支持多种目标平台（至少是这样设计的），因此我们还要把代码分成架构无关部分（arch-independent）和架构相关部分（arch-dependent），对用户层和内核层都是如此。我们在`user`和`kernel`目录下，都有一个`arch`目录，将每个目标的架构相关部分放在各个子目录中，例如与AMD64目标相关的代码就放在`arch/x86_64`。与架构相关的不仅是代码，还有交叉编译器，以及内核镜像在内存中的布局，因此每个架构相关模块还提供两个配置文件：`config.mk`、`layout.ld`。

将系统代码分为架构相关/架构无关的两个模块，并定义它们之间的访问接口，这能让系统更容易移植。如果我们要将Wheel系统迁移到SPARC平台，那么只需要实现SPARC目标的架构相关层。类似的设计在其他系统中同样存在，Windows/Android有平台抽象层（hardware abstraction layer，简称HAL），VxWorks有板级支持包（board support package，简称BSP）。

### 内嵌纯二进制文件

Wheel可以将任意一个文件嵌在内核镜像中，内核代码启动后可直接访问该文件的内容，无需文件系统模块的支持。

将`any.bin`嵌入到内核，首先要使用`objcopy`命令转换为可链接的ELF文件：

~~~ bash
objcopy --input binary --output elf64-x86-64 --binary-architecture=i386 --rename-section .data=.binary any.bin embed.o
~~~

如果不使用`--rename-section`参数，那么在生成的目标文件中，会把二进制文件的内容放在数据段`.data`中。我们在这里改为`.binary`段，因此在内核的连接脚本中就能方便地定位，从而确定二进制文件在内核中的嵌入位置。