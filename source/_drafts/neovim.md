Vim 一直被程序员称为神器，足见其地位之高。然而，最近一个叫做 NeoVim 的项目很引人注目。Vim 编写的时候很早，到现在为止，Vim 中包含了大量的遗留代码，这使得项目的维护、新特性的添加变得越来越困难。

NeoVim 在设计上有许多新的考虑。

Github 的 wiki 上介绍了[安装 NeoVim 的方法](https://github.com/neovim/neovim/wiki/Installing-Neovim)，虽然提供了二进制包，但这并不符合折腾的精神，因此这里说明通过源代码编译安装的方法。

首先下载源代码，通过 Git 克隆项目即可：

``` bash
$ git clone https://github.com/neovim/neovim.git
cd neovim
```

在 Debian/Ubuntu 下，可以通过下面的命令安装依赖项：

``` bash
$ sudo apt-get install libtool libtool-bin autoconf automake cmake g++ pkg-config unzip
```

构建 NeoVim 非常简单，只需要在源码目录下执行 `make` 就可以了。这个 `make` 实际上调用了 cmake。编译完成之后，执行 `sudo make install` 就可以安装了。

默认情况下，NeoVim 会安装到 `/usr/local` 目录下，如果希望安装到其他地方，可以删除 `build/` 目录，然后重新执行 make 并附加一个特殊的环境变量：

``` bash
$ rm -r build/
$ make CMAKE_EXTRA_FLAGS="-DCMAKE_INSTALL_PREFIX:PATH=$HOME/neovim"
```

这样，再次执行 `make install` 的时候，NeoVim 就会安装到其他地方。

配置一下 PATH 环境变量，就可以通过 `nvim` 命令启动 NeoVim 了。

## 配置

打开 NeoVim 之后，会发现界面和 Vim 非常相似。毕竟 NeoVim 的目的就是创造一个与 Vim 兼容的编辑器。

而且，和 Vim 一样，NeoVim 也需要详细的配置才能变得好用。Vim 中的所有按键都能完整地用在 NeoVim 上。

关于 NeoVim 的配置，我在官方网站上还没有找到比较全面的描述，下面的内容都是从一个 [dot nvim](https://github.com/gonglexin/.nvim) 项目中学来的。

Vim 的配置保存在 `~/.vimrc` 文件中，NeoVim 的配置则放在 `~/.nvim/nvimrc` 文件中。

NeoVim 也有插件，而且宣称比 Vim 提供了更好的插件接口。在 Vim 里面，写一个插件需要用 Vim 自己的一套语言，但是在 NeoVim 中，可以用 Lua 和 Python 写插件，这无疑方便了许多。此外，NeoVim 也有插件管理器的概念。在 Vim 中，有 Pathogen、Vundle 这类的工具，在 NeoVim 中，有 NeoBundle，安装方法也很简单：

``` bash
$ git clone https://github.com/Shougo/neobundle.vim ~/.nvim/bundle/neobundle.vim
```

可以看出来，`~/.nvim/bundle/` 目录中保存的就是各个插件，NeoBundle 本身也是一个插件。

#### nvimrc

下面来说一下 nvimrc 文件的写法。

```
set nocompatible
filetype on

nmap ; :
set wrap
set hlsearch
set cursorline	# 突出当前行

set tabstop=4
set softtabstop=4
set shiftwidth=4
set expandtab
```

因为 NeoVim 与 Vim 兼容，原来的 Vim 配置文件还能继续使用。如果已经有 Vim 的配置文件，可以用下面的命令创建两个符号链接：

``` bash
$ ln -s ~/.vimrc ~/.nvimrc
$ ln -s ~/.vim ~/.nvim
```

甚至 `alias vim="nvim"`。

### XDG Configuration

很多 Linux 软件有需要配置文件，而默认配置文件的位置往往是随意指定的，例如某些软件要求配置文件在 `/etc` 目录下，有些放在用户目录下。XDG 标准就是为了规范这些行为而设立的。

NeoVim 遵循 XDG 规范。

- - -

### 配置文件

NeoVim 也需要配置文件。配置文件路径是 `$XDG_CONFIG_HOME/nvim/init.vim`，存储配置文件的目录是 `$XDG_CONFIG_HOME/nvim/`，持久化的 Session 信息保存在 `$XDG_CONFIG_HOME/nvim/shada/main.shada` 文件中。

### 剪贴板

Vim 与系统剪贴板的集成一直不好，NeoVim 要想使用系统剪贴板，需要用到 `xclip` 或 `xsel` 软件，任何一个都可以，只要能在 `PATH` 环境变量中找到就可以。

这样系统的剪贴板是作为 register `+` 和 `*` 存在的，要使用一个 register，可以在 INSERT 模式下输入 `CTRL+R` 然后输入 register 的名称。
