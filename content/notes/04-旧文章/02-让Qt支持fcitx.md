---
permalink: "qt5_with_fcitx"
kind: "article"
tags: ["qt5", "fcitx"]
---

Qt5 有一个让人头疼的问题，就是 Linux 下的中文输入法一直有问题。[这篇文章](http://blog.csdn.net/crazyboy2009/article/details/38537099)给出了一种解决办法，通过复制文件实现，然而发现 Qt 版本 5.4 中此法并不能用，只要尝试启动程序就会段错误。

### fcitx-qt5

在 Github 上有一个 [fcitx-qt5](https://github.com/fcitx/fcitx-qt5) 项目，将这个项目的代码克隆到本地：

``` bash
git clone https://github.com/fcitx/fcitx-qt5.git
```

这是一个使用 CMake 作为构建工具的项目，因此需要保证 CMake 已安装。该项目还依赖 extra-cmake-modules(ECM) 和 XKBCommon 模块，这两个模块通过系统的包管理工具应该都能安装。然而，在 Debian 系统下，extra-cmake-modules 软件包属于 testing 分支下，因此首先需要向 `/etc/apt/source.list` 文件加入一行：

```
deb http://httpredir.debian.org/debian testing main contrib non-free
```

注意其中的版本为 `testing`。修改软件源之后，执行 `sudo apt-get update` 更新缓存，并使用下面的命令进行安装：

``` bash
sudo apt-get -t testing install extra-cmake-modules
```

其中的参数 `-t testing` 表示使用 testing 源中的软件包。

至于 XKBCommon，可以直接用下面的命令安装：

``` bash
sudo apt-get install libxkbcommon-dev
```

### 编译生成

所有依赖项都准备好，接下来使用 Qt Creator 打开项目。使用命令行下的 cmake 来编译也是可以的，但是需要设置 Qt 模块的路径，而使用 Qt Creator 就没有这些问题。

使用 Qt Creator 打开后，在项目右键菜单中选择 Build。编译完成后，会在 `fcitx-qt-build` 目录下看到最终的输出文件。

为了使程序能够使用 fcitx 输入中文，需要将以下三个文件夹和其中的文件复制到可执行文件目录下：

```
.
├── dbusaddons
│   ├── libFcitxQt5DBusAddons.so -> libFcitxQt5DBusAddons.so.1
│   ├── libFcitxQt5DBusAddons.so.1 -> libFcitxQt5DBusAddons.so.1.0
│   └── libFcitxQt5DBusAddons.so.1.0
├── platforminputcontext
│   └── libfcitxplatforminputcontextplugin.so
└── widgetsaddons
    ├── libFcitxQt5WidgetsAddons.so -> libFcitxQt5WidgetsAddons.so.1
    ├── libFcitxQt5WidgetsAddons.so.1 -> libFcitxQt5WidgetsAddons.so.1.0
    └── libFcitxQt5WidgetsAddons.so.1.0
```

将这些文件复制到程序所在目录之后，就能使用搜狗输入中文了。

### Qt Creator

Qt Creator 稍稍复杂一些，需要将上面生成的三个目录放在两个地方。首先需要把它们放在 Qt Creator 的安装位置中的插件目录下，通常是 `/opt/Qt/Tools/QtCreator/bin/plugins`。此外，还要将那三个目录复制到 Qt 安装目录下的全局插件目录中，通常地址是 `/opt/Qt/5.4/gcc_64/plugins`。

需要注意的是，可能需要将 `platforminputcontext` 改名为 `platforminputcontexts`。

最后还有一点，就是 Qt Creator 中 `Ctrl+Space` 是代码提示的快捷键，这与输入法切换的组合是冲突的，解决办法也很简单，到 Qt Creator 内修改快捷键设置，将其设为别的组合或者直接禁用。这样操作之后，就可以在 Qt Creator 中使用搜狗输入法打中文了。

### Final

上面的解决方法似乎不太稳定，时好时坏。

使用 `dpkg -L` 命令查看 `fcitx-frontend-qt5` 的安装文件，其中最后一行是 “/usr/lib/x86_64-linux-gnu/qt5/plugins/platforminputcontexts/libfcitxplatforminputcontextplugin.so”，把这个文件连带 `platforminputcontexts` 目录复制到可执行文件的目录下，让可执行文件和 `platforminputcontexts` 位于同一级别，没有 `plugins` 目录。这样启动目标程序可以使程序支持搜狗输入法。

注意，fcitx-qt5 项目编译出来的目录中有一个子目录名为 `platforminputcontext`，需要在其后加上一个 `s`，才能正常工作。

### Linux 输入法

受到这个问题的启发，我深入地了解了以下 Linux 下的输入法架构。

要了解 Linux 下的输入法，需要首先明确两个概念——输入法框架和输入法引擎：

- 输入法框架（framework）是一个 Daemon，负责接受用户的键盘输入，并将输入结果发送给目标应用程序。
- 输入法引擎（engine）是一个程序，负责分析用户的按键动作，给出一系列可能的结果，并把这些结果发送给输入法框架。

总结起来，就是框架负责事件处理和通信，引擎进行思考。所有能看到的地方——面板、配置界面——都是框架的一部分，而引擎的工作都是看不见的。

正是因为 Linux 将 framework 这部分暴露出来，所以才有了各种不同的输入法引擎。

IBus 是许多 Linux 发行版的默认输入法框架，这是因为 IBus 是基于 GTK+ immodule 模块编写的，因此对 GNOME 桌面有完美的支持。目前由一名北大学生 Huang Peng 维护。项目地址：(https://github.com/ibus/ibus)。

IBus 还有一个子项目——ibus-pinyin，这也是很多 GNOME 上的默认拼音输入法。最初使用 Python 写的，现在已经用 C++ 重写。

参考：[Linux input method framework brief summary](https://blogs.gnome.org/happyaron/2011/01/15/linux-input-method-brief-summary/)

### Qt 中的输入法

[KDAB 上关于这部分的介绍](http://www.kdab.com/qt-input-method-depth/)

假设我们要创建一个自定义的 Widget，这个 Widget 支持文字输入。我们当然不希望用 keyEvent 来接受键盘事件，因为这样只能输入英文，这是就需要 Qt 的输入法支持。

至于 Qt 如何与输入法框架/引擎不在我们的考虑范围内，我们只关心如何使用。要让一个 Widget 与输入法配合起来，首先需要向输入法提供一些信息，其次需要从输入法接收一些信息。

但是在这之前，需要设置一个 Attribute：

``` c++
setAttribute(Qt::WA_InputMethodEnabled, true);
```

这样，Qt 才会认为这个 Widget 需要输入法支持。

还有一个很重要但是经常忽视的地方，只有 focus 的 widget 才能接收按键事件。因此最好设置为：

``` c++
setFocusPolicy(Qt::ClickFocus);
```

接收输入法输入信息用的函数是 `inputMethodEvent(QInputMethodEvent*)`，参数是 `QInputMethodEvent` 类型的指针，该类型包含 4 个属性：
- `preeditString`，通常是用户输入了还没有提交的内容，显示在输入法的面板中
- `commitString`，用户提交的内容，需要显示在控件中
- `replacementStart` 和 `replacementLength`，这两个属性表示需要将 preeditString 中的那一部分替换掉

实验发现，后两个参数总是为0，而且输入法会在自己的面板上显示 `preeditString` 的内容，因此实际上控件只需要检查 commitString 的内容并将其插入到光标位置。
