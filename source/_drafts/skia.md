---
title: Skia 图形库
---

Skia 是 Google 的一款二维向量图形库，Chrome 和 Android 都是使用 Skia 绘制图形界面。

### 安装

Skia 需要 depot_tools，里面有 Google 常用的一些工具，因此首先要把 depot_tools 装好。

``` bash
$ git clone 'https://chromium.googlesource.com/chromium/tools/depot_tools.git'
$ export PATH="${PWD}/depot_tools:${PATH}"
```

注意导出的 PATH 环境变量需要把 depot_tools 放在最前面，因为 depot_tools 的某些命令可能和系统命令重名。

接下来就可以下载 Skia 源码了。

``` bash
$ git clone https://skia.googlesource.com/skia.git
$ cd skia
```

下载完成之后，运行其中的 Python 脚本同步依赖项，并编译程序：

``` bash
$ python bin/sync-and-gyp
$ ninja -C out/Debug
$ out/Debug/dm
```

如果希望使用 clang 而不是 gcc 来编译，可以把第一步的命令换成 `CC='clang' CXX='clang++' python bin/sync-and-gyp`。

如果不需要大堆测试程序，只想生成一个库文件，可以这样 `ninja -C out/Release skia_lib`。Skia 生成的库都是静态链接库，Skia 并不支持动态链接。而且 Skia 生成的动态库是许多个，

## 使用 Skia

官网上的 [Building with Skia Tutorial](https://skia.org/user/sample/building) 给出了使用 Skia 的方法，但是要用到 gclient、gyp 等工具，很不习惯，于是尝试一下不用 depot_tools 使用 Skia 的方法。

首先准备一个项目，比如叫做 skia_

编译命令：

``` bash
$ clang++ -c main.cpp -std=c++11 -I../skia/include/config -I../skia/include/core -o main.o
```

链接的命令是：

``` bash
clang++ main.o -L../skia/out/Release/ -L../skia/out/Release/obj/gyp/ -Wl,--start-group -lskia_core -lskia_animator -lskia_effects -lskia_images -lskia_opts -lskia_opts_sse41 -lskia_opts_ssse3 -lskia_pdf -lskia_ports -lskia_sfnt -lskia_skgpu -lskia_skgputest -lskia_svg -lskia_utils -lskia_views -lskia_xml -letc1 -lexperimental -lflags -llua -lresources -lsk_tool_utils -l views_animated -ljpeg -lSkKTX -lwebp_dec -lwebp_demux -lwebp_dsp -lwebp_enc -lwebp_utils -lskflate -Wl,--end-group -lpng -lz -lgif -lpthread -lfontconfig -ldl -lfreetype -lGL -lGLU -lX11
```

### Skia With CMake

~~在 Skia 源码的 cmake 目录下，有一个 `CMakeLists.txt` 文件，可以作为一个样板。~~这个文件是编译 Skia 用的。
