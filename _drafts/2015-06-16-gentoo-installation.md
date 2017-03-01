title: Gentoo Linux 安装
---

Gentoo 是一个很有个性的 Linux 发行版，就连安装也非常特别。Gentoo 没有提供安装工具，用户充当了安装器的角色。这样做虽然麻烦，但是安装完成之后，能大大加深使用者对 Linux 的理解。

### 宿主环境

安装 Gentoo 需要进行磁盘分区、复制文件等一系列操作，这些操作显然不能在裸机上进行，因此需要一个宿主系统，通常也是一个 Linux。Gentoo 官网提供了 Live 镜像，目的就是让用户有一个能运行起来的 Linux 环境，方便在此之上进行安装。千万不要被 LiveCD 的名字欺骗，只用它没法装上 Gentoo。

如果电脑上已经装有 Linux，也可以在原来的 Linux 下进行，省去制作 Live 启动盘的麻烦。本文叙述的步骤就是在 Debian 下进行的。

### 磁盘分区

要把 Gentoo 装到硬盘上，首先要准备一个分区，并格式化为 Gentoo 支持的格式。这里我使用 GParted 创建一个 `/dev/sda12` 逻辑分区，格式化为 ext4 文件系统，如下图所示。

![磁盘分区](/images/gentoo-partition)

这里我只给 Gentoo 分配了一个分区，如果有必要，可以创建额外的分区用作 `/boot`、`/home` 等目录的挂载点。分区完毕，将分区挂载：

```
sudo mount /dev/sda12 /mnt/gentoo
```

如果为 `/boot`、`/home` 等目录创建了额外的分区，则也要挂载上。

### 准备 Stage3

下面需要准备安装文件了，在[这里](https://www.gentoo.org/downloads/mirrors/)选择一个镜像站，进入其 `releases/amd64/autobuilds` 目录下，选择名为 `stage3-amd64-*.tar.bz2` 的文件下载。并使用下面的命令解压：

``` bash
cd /mnt/gentoo
tar xvjpf stage3-*.tar.bz2 --xattrs
```

解压完成后，会看到标准 Linux 系统的目录结构已经创建好了：

``` bash
bin   dev  home  lib32  media  opt   root  sbin  tmp  var
boot  etc  lib   lib64  mnt    proc  run   sys   usr
```

接下来，配置软件源。和其他发行版一样，Gentoo 也有自己的软件仓库，全球分布多个镜像站。选择某个镜像，只需编辑 `/etc/portage/make.conf`，添加一个 `GENTOO_MIRRORS` 变量，取值是一个字符串，字符串内容是镜像站地址，多个地址用空格区分，就像这样：

```
GENTOO_MIRRORS="http://mirrors.163.com/gentoo/ http://mirrors.xmu.edu.cn/gentoo"
```

### 选择 Profile

```
eselect profile list
```

这样会显示出所有支持的 profile，选择其中编号为 i 的条目，使用命令：

```
eselect profile set i
```

这里选择 `default/linux/amd64/13.0/desktop/gnome`

### 杂记

chroot 之后，发现 emerge 总是更新失败，后来发现是域名无法解析，在后来发现 ping 任何网址都不行。于是，在 Debian 下找出 `/etc/resolv.conf` 的内容，并写入 chroot 环境下相同的文件中，相当于手动指定 DNS 服务器的地址。这样之后，再执行 emerge 更新就能成功了。
