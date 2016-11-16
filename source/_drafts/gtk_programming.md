---
title: GTK+ 编程
category: "开发"
tags: ["gtk", "linux"]
---

随便在网上搜一下“GTK+ and Qt”，似乎结果都是 Qt 如何如何的优于 GTK+。但是作为一款流行的工具库，GTK+ 还是非常优秀的。

> 其实背后的原因是，GTK+ 的移植难度看似低于 Qt，今后有望作为 Wheel 的界面开发库。

### 安装和基本使用

在 Linux 上，最好使用发行版的包管理工具安装 GTK+，另外为了方便编译，最好安装 PkgConfig。在 Debian/Ubuntu 上，可以用这条命令：

``` bash
$ sudo apt-get install libgtk+-3.0 pkg-config
```

安装完成之后，可以编写一个简单的 GTK+ 应用程序测试一下：

``` c
#include <gtk/gtk.h>

static void activate(GtkApplication* app, gpointer user_data) {
    GtkWidget *window = gtk_application_window_new(app);
    gtk_window_set_title(GTK_WINDOW(window), "Window");
    gtk_window_set_default_size(GTK_WINDOW(window), 200, 200);
    gtk_widget_show_all(window);
}

int main(int argc, char *argv[]) {
    GtkApplication *app = gtk_application_new("org.gtk.example", G_APPLICATION_FLAGS_NONE);
    g_signal_connect(app, "activate", G_CALLBACK(activate), NULL);
    int status = g_application_run(G_APPLICATION(app), argc, argv);
    g_object_unref(app);
    return status;
}
```

编译的方法如下：

``` bash
$ gcc -o gtk gtk.c `pkg-config --cflags --libs gtk+-3.0`
```

### 号外：在 Windows 上配置 GTK+ 3.0 开发环境

实践证明，在 Windows 上开发 GTK+ 程序是完全可以的，而且非常容易。

这里要用到 MSYS2，这是和 Cygwin、MSYS 类似的一个东西，也提供了一个兼容 Unix 的环境，而且还提供了 Arch Linux 的包管理工具 pacman。

hippocampus

如何在WIndows系统上配置Gtk+3.0开发环境

安装MSYS2，这是一个新的Unix环境，其中包含了Arch Linux用的Pacman软件包管理工具。按照MSYS2官方网站上的说明，同步Pacman的软件源，安装一些基本工具。

使用下面的命令安装mingw、gcc：

pacman -S mingw-w64-i686-toolchain

默认装好的软件位于C:/msys2/mingw32/bin以及C:/msys2/mingw32/i686-w64-mingw32/bin目录下，但是这些目录默认不在PATH中，因此需要将这些目录加到PATH环境变量里。

此外，为了开发GTK程序，另外两个软件包需要安装：mingw-w64-i686-gtk3、pkg-config

但是装好的pkgConfig需要一个环境变量PKG_CONFIG_PATH，只有在这个环境变量中的目录才会被探测到。默认的PKG_CONFIG_PATH并不正确，有一个重要的目录/mingw32/lib/pkgconfig/并未添加至其中。MSYS2中安装的软件，包括GTK3在内，都会在这个目录下创建一个pc文件，这些pc文件正是PkgConfig需要的配置文件，因此需要将/mingw32/lib/pkgconfig/添加到PKG_CONFIG_PATH之中。由于这个环境变量每次都要用到，因此最好写在.bashrc文件中：

export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:/mingw32/lib/pkgconfig/"

另外一个问题，在Windows XP上测试GTK3的时候，出现错误：mingw32/bin/gtk-query-immodules-3.0.exe: error while loading shared libraries: ? cannot load ...

找到出问题的exe文件（上面的例子中是gtk-query-immodules-3.0.exe），然后双击运行，看一下提示的错误信息，发现是找不到dwmapi.dll，于是从网上下载一个dwmapi.dll文件，放进C:/Windows/system32，再次运行程序，就一切正常了。

网上下的dwmapi.dll有很多种版本，如果使用的版本不合适可能运行程序后显示“无法定位输入点…于dwmapi.dll”，只要使用的是正确版本的dwmapi.dll就不会有这个问题。

MSYS2环境中，编译器可以选择gcc，也可以选择mingw-w64-i686-gcc。cmake可以直接安装cmake，也可以安装mingw-w64-i686-cmake，它们的区别就是能够脱离MSYS2运行。如果采用Unix工具构建而成，那么生成的EXE文件只能够在MSYS2环境下运行，如果使用mingw系列的工具构建（即使用/mingw32/bin/cmake生成VS工程，VS编译），那么最终的可执行文件是可以直接双击运行的。

========================================

使用VS编译会遇到找不到引用的gtk.h头文件的问题，这是因为工程使用Cmake生成，而cmake中用到了PkgConfig来确定gtk的头文件、编译参数、连接选项等。如果使用VS，那么使用的是VC++编译器，编译参数的格式和PkgCOnfig生成的不一样，因此不能用。

不过，通过MSYS2装好了一大堆的mingw工具，这些工具是在MSYS2之外也能用的，因此可以打开一个原始的命令提示符，在其中使用cmake生成一个“MinGW Makefiles”的项目（不能在MSYS2中进行，因为对于MinGW，要求sh.exe不能在PATH之中）。然后使用mingw32-make来编译。
