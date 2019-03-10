---
title: "VxWorks源码分析（一）"
---

由于项目关系，有幸接触到了 VxWorks 6.7 的源代码，于是带着膜拜的心态开始阅读并分析其源代码，并将分析的结果记录在这里。

国内关于 VxWorks 的资料比较少，而且网上找到的资料不少是针对 VxWorks 5.x 的，和旧版比起来，VxWorks 6.x 增加了对多核硬件（SMP）的支持，并且加入了实时进程（RTP），可以开发用户态的应用程序，代码上的区别还是很大的。

### 文件组织结构

VxWorks 并不是一个开源的操作系统，其源代码通常是随着开发套件一起安装的。VxWorks 的开发 IDE 是 Workbench，基于 Eclipse 定制，与源代码和其他辅助工具一起构成风河开发套件。假设风河开发套件安装在 `C:\WindRiver`，那么 VxWorks 6.7 的源代码位于 `C:\WindRiver\vxworks-6.7\target`。其中有如下子目录：

> - `config`：这个目录中包括所有的 BSP
>     - `comps/vxWorks`：包含系统默认的组件定义文件（CDF）
>     - `comps/src`：这个目录下包含 configlettes，也就是一些短小的配置代码
> - `h`：VxWorks 内核头文件
>     - `private`：私有头文件，只有 `src` 中的代码能够访问
>     - `make`：Makefile 片段文件，这些文件会被各个工程的 Makefile 中引用
>     - `tool`：包含与工具链相关的 Makefile 片段，以及链接脚本
> - `src`：VxWorks 内核的源文件
> - `lib`：这个目录保存编译生成的内核库（单核版本）
> - `lib_smp`：这个目录保存编译生成的内核库（多核版本）
> - `usr`：所有用户态相关的文件都放在这里（RTP）
>     - `h`：用户态代码使用的头文件
>     - `src`：用户层库的源文件
>     - `lib`：保存编译生成的用户库

下面对代码结构中涉及到的一些概念进行解释：

- **BSP（board support package）**。VxWorks 是一个跨平台的操作系统，可以运行在 x86、PowerPC、ARM 等多种架构的硬件上。系统的核心代码是通用的，然而操作具体硬件的代码无法通用。因此将硬件相关的代码从系统中剥离出来，组成一个单独的模块，称作 BSP，每种硬件设备对应一个 BSP。针对某个设备构建系统，只需要将这个设备的 BSP 与通用代码一起编译即可；同时移植系统到新设备也更容易，只需要为这个新设备开发一套 BSP 即可。BSP 代码位于 `target/config` 目录下，每个子目录都表示一个 BSP。
- **组件和组件定义文件**。VxWorks 是一个可定制化程度很高的系统，定制的单位就是组件（component）。每个组件都实现了某种功能，开发者可以根据项目的具体需求，决定添加哪些组件到系统中来。将更多的组建添加到系统中，可以让系统具有更多功能；将不需要的组件移除系统，能让生成的系统镜像更小，运行速度更快。Workbench 提供了一个图形化配置工具，通过它可以方便地配置项目中使用的组件，Workbench 会自动管理组件之间的依赖关系。组件的名称、相互依赖关系，以及配置项和 configlette 等信息被保存在组建定义文件（component definition file，简称 CDF）中，Workbench 正是通过 CDF 文件分析出系统中每个组件的信息，并给用户提供一套管理界面。CDF 文件位于 `target/config/comps/vxWorks` 目录下，后缀名为 `*.cdf`。
- **configlette**。从字面上看，configlette 的意思就是“小配置文件”，本质上就是一个代码文件。之所以要把这些代码特殊对待，是因为代码中使用了一些配置项，这些配置项只有在用户完成系统定制之后才能确定最终取值，在编译内核库的时候尚不能确定（关于内核库与构建流程将在后面介绍）。configlette 文件保存在 `target/config/comps/src` 目录下。

VxWorks内核的源代码就放在 `src` 目录下，这个目录下面又有许多子目录，按不同的功能模块组织分类。由于 VxWorks 系统经历过无数次的升级改进，`src` 下的内容显得有些凌乱，以下是几个核心子目录：

> - `arch`，体系架构相关代码，例如 `arm`、`ppc`、`x86` 等
> - `os`，包含系统核心代码，包括类和对象、内存管理、输入输出，以及 RTP
> - `wind`，包含任务管理和调度、信号量、消息队列。许多重要的内核 API 都定义在这个目录下
> - `drv`，传统驱动程序代码
> - `hwif`，这个目录下包含 VxBus 框架的驱动程序代码
> - `util`，包含一些通用数据结构和工具库的定义，例如AVL平衡树、链表、优先队列等，这个目录下定义的许多数据结构被其他模块使用

比较重要的两个是 `wind` 和 `os`。`wind` 目录下包含任务管理相关代码，`os` 下则包含对象系统、内存管理等内容。这两个目录的功能看起来有些重合，区别在于，`wind` 模块提供的是公开的内核 API，函数接口是稳定的，而 `os` 模块提供的则是私有函数，供其他的 VxWorks 内核代码使用，风河不保证函数接口在不同系统版本之间保持一致。

从代码文件的命名方式上，就能大概看出属于哪个组件。例如内存管理组件 memPartLib，相关代码包括 `src/os/mm/memPartLib.c`、`h/memPartLib.h`、`h/private/memPartLibP.h`，其中 `h/private` 中的头文件是私有头文件，风河不保证私有头文件中的函数接口发生改变，因此开发者为了确保与后续版本的 VxWorks 兼容，在开发中应该使用 VxWorks 的公开 API。

VxWorks 将类似功能的组件代码放在同一个目录下，每个目录下还有一个 `Makefile` 文件，这个文件用来指导 VxWorks 内核的编译过程。需要说明的是，编译 VxWorks 内核生成的不是完整 OS，而是**内核库**，要创建一个完整的 OS，需要得到内核库之后创建 VIP 项目，下一节会有详细说明。

### VxWorks 的常规开发流程

平时我们讲 Linux 开发，通常意思是在 Linux 系统之上进行开发应用程序，同时开发出来的应用程序也运行在 Linux 系统上。然而 VxWorks 是一个嵌入式系统，我们不方便在 VxWorks 中进行开发，一般而言，VxWorks 开发工作是在一个运行着 Linux 或 Windows 的开发机上进行的，在开发机上编译之后，再把生成的东西放在开发板上运行。而且编译出来的也不是应用程序，而是一个系统镜像（system image），这个系统镜像可以直接加载到开发版上，或者烧录到设备 ROM 中。

这种系统镜像类型的项目叫做 VIP（VxWorks Image Project），它产生的输出就是一个完整的 OS。而且 VxWorks 的可定制成都很高，开发者可以选择这个 OS 中需要哪些功能，不需要那些功能，还有相关配置参数的取值。开发工具会根据用户的配置，生成一个定制的系统镜像。

VIP 项目的构建过程其实非常简单，就是把相关的静态库链接在一起。由于静态库实际上就是若干目标文件的打包，因此静态库链接就相当于把一对目标文件链接在一起。根据 VIP 项目中的用户配置，开发工具可以选择链接哪些目标文件，不链接哪些目标文件，这就实现了系统功能的定制。（当然，VIP 构建过程肯定不是只有链接，BSP代码、开发者编写的代码、根据 VIP 配置自动生成的代码，这些都需要进行编译，并于内核库共同链接。）

因此，构建 VIP 项目之前，需要保证所需静态库存在，这些静态库就是**内核库**，通过编译 VxWorks 内核源代码生成。编译内核库有两种方式：

- 通过命令行，在 `src` 目录下执行 `make CPU=PENTIUM TOOL=gnu VXBUILD=SMP` 命令来编译（当然，需要根据具体的目标平台、编译器和多核选项来调整构建参数）。这种方式生成的静态库会保存在 `lib` 或 `lib_smp` 目录下（取决于单核还是多核）。
- 通过集成开发环境 Workbench，创建 VSB（VxWorks Source Build）项目，构建 VSB 项目来编译内核库。这样生成的内核库会位于 VSB 项目目录中。

风河之所以将编译 VxWorks 的过程分为两步，一个原因是这可以加快 VIP 项目的构建速度，另一个原因则是用户可以在没有源代码的情况下使用 VxWorks 开发。用户可以创建 BSP 项目开发自己的版级支持包，也可以创建 VIP 项目，编写自己的内核应用程序，但是系统核心部分的代码是不变的。因此首先把系统核心部分编译成静态链接库，这样在构建 BSP 项目时就可以直接链接已经生成的库。

### 内核库的编译过程

前面已经分析了，VxWorks 系统镜像的构建需要已经编译完成的内核库。而内核库正是 `target/src` 目录下的代码，俗称的 VxWorks 系统源代码，实际上就是内核库的源代码。编译内核库是通过 make 工具完成的，首先运行的是 `target/src/Makefile` 文件，这个文件又会递归调用 make 执行子目录下的 Makefile 文件，最终遍历到所有子目录。如果分析一下这些 Makefile 文件，会发现它们基本上都有这样的内容：

~~~ Makefile
include $(TGT_DIR)/h/make/defs.library
include $(TGT_DIR)/h/make/rules.library
~~~

这两行引用了 `target/h/make/defs.library` 和 `target/h/make/rules.library` 两个文件，分别包含编译过程需要的变量定义和规则定义，相当于把相同的逻辑提取了出来，每个子目录只需要引用这些文件，并定义自己的变量即可。

概括起来，每个源码目录的编译过程非常简单，变量 `OBJS` 指定了需要编译的目标文件列表，变量 `SUBDIRS` 指定了需要递归执行 make 命令的子目录，如果 `SUBDIRS` 没有定义，那就遍历所有的子目录。也就是说，`OBJS` 决定了当前目录下的哪些文件需要编译，`SUBDIRS` 则决定哪些子目录需要递归。

每个子目录为一个单位，其中的所有目标文件会在编译完成后打包成一个静态库文件。静态库本质上就是一些目标文件组成的压缩包，因此编译内核库的过程就是将 `target/src` 目录下的每一个源文件编译成目标文件，存放在 `target/lib_smp` 中。

### 组件配置系统

VxWorks 系统中的各个组件都是可以选择添加的，用户通过 Workbench 可以对系统镜像项目中使用的组件进行配置。组件的配置情况并不会决定哪些文件参与编译，毕竟在构建系统镜像之前，内核库就已经编译完成了。组件的配置情况决定的是系统的启动过程，如果启用了某一个组件，那么就会在系统启动阶段调用这个组件的初始化函数。

组件配置情况通过四个文件体现出来：`prjComps.h`、`prjParams.h`、`prjConfig.c` 和 `linkSyms.c`。

前两个头文件 `prjComps.h`、`prjParams.h` 通过宏定义了当前配置下启用的每一个组件，并通过宏定义了用户配置的组件参数。这些宏会被 `prjConfig.c` 和 configlette 文件使用，正是因为使用到了构建镜像时才有的宏，configlette 被强行从内核源代码中分离出来，不和内核库一同编译，而是作为 VIP 项目代码的一部分。

`prjConfig.c` 则包含系统启动过程中执行的一系列函数，包括多任务环境启动之前执行的 `usrInit`，以及多任务启动之后，以第一个任务身份运行的函数 `usrRoot`。大量的组件都需要多任务环境，因此主要在 `usrRoot` 函数中初始化，而在多任务环境尚未建立的时候，只有一些基础核心组件可以初始化，如 cacheLib、objLib、objOwnerLib、objInfo、classLib、classListLib 等。

`linkSyms.c` 的内容则比较简单，定义了一个巨大的函数指针数组。由于在链接的时候，链接器会检查每个目标文件的引用数量。如果一个目标文件中没有函数会变量被其他文件引用，那么就说明这个目标文件是多余的，链接器便会把这个目标文件从最终的镜像文件中删除，以减小镜像文件的大小。然而有的时候，我们确实需要一些函数留在镜像中。链接的时候没有引用，并不表示运行时这个函数也不需要，更何况 VxWorks 允许用户通过命令行直接调用函数，还支持内核模块动态加载。为了避免一些关键模块被链接器优化掉，我们定义一个函数指针数组，将那些链接时没有引用但是又非常重要的函数放在数组中。这样强行添加一个引用，模块的引用数量就不再是零了，也就不会被链接器删除。

### VxWorks 系统启动过程

在介绍 VxWorks 启动过程之前，首先补充一下系统镜像工程（VxWorks Image Project，VIP）的几种 Build Spec：

- `default`：默认选项，生成的镜像不含 bootloader 代码，需要专门的程序加载到 RAM 中才能运行。
- `default_rom`：生成的镜像包含 bootloader 代码，可以加载到 ROM 中，内部的 bootloader 会自动复制内核到 RAM 并运行。
- `default_romCompress`：类似 `default_rom`，但是对镜像进行了压缩，体积更小，复制到 RAM 之前需要解压。
- `default_romResident`：类似 `default_rom`，但是系统镜像不需要复制到 RAM，可以直接在 ROM 中运行。

包含 bootloader 的镜像可以直接烧录到设备 ROM 中，适合于生产环境。不包含 bootloader 的镜像需要专门的引导器程序启动，但不需要烧录 ROM，可以网络引导，适合于开发环境。bootloader 代码位于 BSP 中的 `romInit.s` 文件内，负责将保存在 ROM 中的系统镜像复制到 RAM 中，如果启用了压缩，还需要对系统镜像解压。然后跳转到内核的入口点开始执行。bootloader 程序的入口点是 `romInit`，内核入口点是 `sysInit`。不管是否使用 bootloader，对内核而言，启动的过程是完全一致的。

#### sysInit

这个函数是 VxWorks 内核镜像最先开始运行的函数，代码位于 BSP 目录下的 `sysALib.s` 汇编文件中。源文件中，有着关于本函数功能的一段注释：

> This is the system start-up entry point for VxWorks in RAM, the first code executed after booting. It disables interrupts, sets up the stack, and jumps to the C routine usrInit() in usrConfig.c.

可以看出，本函数的主要工作就是禁用中断、设置函数栈，然后跳转到 `usrInit` 函数，开始执行 C 语言代码。

如果分析以下 VIP 项目生成的系统镜像文件，就会发现 `sysInit` 函数位于代码段的开始位置，也就是 VxWorks 内核被加载到的位置。这个位置由宏 `RAM_LOW_ADRS` 控制，表示内核被加载到的位置。由于函数 `sysInit` 就位于内核镜像的开头位置，bootloader 与开发工具都能够非常方便地找到这个函数的地址，并控制 CPU 跳转过去。

当函数 `usrInit` 开始执行时，按顺序执行下列操作（`usrInit` 的执行过程与具体的处理器架构关系非常紧密，下面给出的是 SPARC 架构的情况）：

- 禁用中断，通过写 `PSR` 寄存器，屏蔽 ET（Enable Trap）位实现。
- 加载 trap table，将 trap table 的地址写入 `TBR` 寄存器。
- 初始化寄存器窗，写 `WIM` 寄存器。
- 初始化所有的通用寄存器，包括每个窗之内的 local 与 input 寄存器。
- 启用 cache snooping，使用硬件机制保证 SMP 环境下的缓存一致。
- 将 trap tabl 复制到 8KB 之前的位置，并重新加载 `TBR`。若之前 `TBR` 位于 `0x40003000`，则复制之后位于 `0x40001000`。
- 调用函数 `_leon23_checkcpu`，初始化 `_nwindows` 和 `_nwindows_min1` 变量。
- 最后跳转到 `usrInit` 函数中开始执行。

#### usrInit

这个函数是系统中最早开始运行的 C 语言代码，位于 VIP 项目下的 `prjConfig.c` 文件中，函数的代码由 Workbench 自动生成。

这个函数运行的时候，多任务环境尚未建立，因此在这一阶段，只能对一些不依赖多任务的模块进行初始化。例如 cacheLib、objLib、objOwnerLib、objInfo、classLib、classListLib 这些模块，都不依赖多任务，因此可以在 `usrInit` 中进行初始化。基本类和对象相关的模块都在这一阶段初始化，因为类和对象是 VxWorks 其他模块的基础，而且并不需要多任务环境。

除了初始化类和对象相关模块，在 `usrInit` 函数中还执行了如下操作：

- 调用 `sysStart` 函数，该函数将 bss 段清零，使之符合 C 语言的规范。
- 调用 `usrCacheEnable`，启用指令缓存和数据缓存。
- 调用 `usrKernelInit`，这个函数负责初始化任务管理，配置多任务环境，并且启动系统的第一个任务。

#### usrKernelInit

这个函数位于 `target/config/comps/src/usrKernel.c`，由 `usrInit` 调用，执行过程为：

- 调用 `kernelLockInit`，初始化内核锁
- 调用 `taskLibInit`，初始化任务管理模块
- 配置调度策略
- 初始化 work queue，这是一个用于记录异步操作的队列
- 填充 `_KERNEL_INIT_PARAMS` 结构体，并调用 `kernelInit` 启动多任务
- 因此主要的启动工作是在 `kernelInit` 函数中进行的。在 `_KERNEL_INIT_PARAMS` 结构体中，指定根任务的入口点为 `usrRoot` 函数

#### kernelInit

这个函数在 `usrKernelInit` 中调用，实现位于 `src/wind/kernelLib.c` 文件中。这个函数设置了内存分区，创建根任务的 TCB 对象，并且开始运行第一个任务。具体执行过程为：

- 根据 SMP/UP 以及不同硬件栈的生长方向，划分系统的内存区域
- 如果是 SMP，为每个处理器准备一个 `tIdleTask` 任务
- 为根任务和每个处理器的 Idle 任务准备执行栈和异常栈，这些栈所使用的内存空间直接从系统的可用内存中划分。这里不能使用内存管理模块进行分配，因为此时内存管理功能尚不可用
- 调用 `taskInitExcStk` 初始化根任务和每个处理器的 Idle 任务
- 调用 `taskActivate`，启动根任务

#### usrRoot

`usrRoot` 函数是根任务的入口点，因此 `usrRoot` 执行时，VxWorks 的多任务执行环境已经建立，此时所有模块都可以初始化。

`usrRoot` 的实现位于 VIP 项目自动生成的 `prjConfig.c` 文件中，调用了大部分库的初始化函数。由于不同的 VIP 配置会导致不同的初始化步骤，因此 `usrRoot` 函数的内容在不同的 VIP 项目里存在一定差异。此外由于 `projConfig.c` 文件是 Workbench 自动生成的，因此不建议开发者手动编辑该文件。

在 `usrRoot` 函数的最后，通常会调用 `usrAppInit`，执行用户编写的入口函数。`usrAppInit` 就相当于实时系统的 main 函数，用户编写的代码从这里执行。当函数 `usrAppInit` 退出之后，根任务便结束运行，但用户如果在 `usrAppInit` 中创建了新的任务，那么新创建的任务便会在根任务生命周期结束之后开始运行。到此 VxWorks 系统的初始化过程结束。