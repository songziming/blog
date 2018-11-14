---
title: "使用 LD_PRELOAD 拦截库函数调用"
kind: "article"
tags: ["hook", "Linux"]
---

`LD_PRELOAD` 是 Linux 下一个很有意思的环境变量，通过这个变量，可以在运行程序时强制加载某个动态库，而且是最先加载。通过 `LD_PRELOAD` 可以非常方便地拦截库函数的调用，而且不需要修改可执行程序。

### 例子：拦截 strlen

下面通过一个例子来演示使用 `LD_PRELOAD` 拦截 `strlen` 的方法。首先是一段测试代码：

``` c
#include <stdio.h>
#include <string.h>
int main(int argc, char *argv[]) {
    char s[] = "hello, world!";
    printf("length is %d\n", strlen(s));
    return 0;
}
```

编译生成可执行文件 `test`，运行，输出 `length is 13`，没有问题。

下面创建一个 `hook.c` 文件，里面包含另一个 `strlen` 实现：

``` c
#include <string.h>
size_t strlen(const char *str) {
    return 4;
}
```

这个版本的 `strlen` 不管输入什么都会返回 4。用下面的命令编译 `hook.c`：

``` bash
$ gcc -shared -fPIC hook.c -o hook.so
```

这样，就生成了 `hook.so`，其中包含着一个盗版的 `strlen` 函数，接下来通过下面的命令运行刚才的程序：

``` bash
$ LD_PRELOAD=$PWD/hook.so ./test
```

这一次运行程序，输出结果变成了 `length is 4`，这说明 `strlen` 函数确实被替换了。

### 实现机制

首先我们分析一下正常的情况。程序中使用了 `strlen` 函数，而这个函数是 C 语言标准库中提供的，通过 `ldd test`，我们可以看到 `test` 文件执行所需的动态库：

```
linux-vdso.so.1 (0x00007fffda2b4000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007f1da8a15000)
/lib64/ld-linux-x86-64.so.2 (0x00007f1da8dbe000)
```

其中 `libc.so.6` 就是 Linux 下的标准 C 库。一个可执行文件运行的时候，系统会预先加载所需的动态库文件，当可执行文件 `test` 的镜像加载时，系统会进行动态绑定（也叫重定位），将 `test` 中对 `strlen` 的调用与 `libc.so.6` 中的符号 `strlen` 关联起来，库函数的调用从而可以正常执行。

环境变量 `LD_PRELOAD` 的作用就是在加载其他的动态库之前，如果这些库中也定义了某些程序用到的函数，它们就会优先与可执行文件匹配。

因此，`hook.so` 中定义了 `strlen`，优先于 `libc.so.6` 与 `test` 中的调用匹配，因此后一次运行的时候输出了错误的字符串长度。

### 实现功能透明

通常进行库函数拦截是为了进行监控和统计，功能上要保持一致。因此，在假的库函数中，应该调用真的库函数完成相应功能，例如：

``` c
#include <string.h>
size_t strlen(const char *str) {
    return real_strlen(str);
}
```

现在的问题变成了如何确定 `real_strlen`，方法就是，通过 Linux 下的动态链接器。

``` c
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>

typedef size_t (*strlen_t)(const char *str);
size_t strlen(const char *str) {
    strlen_t real_strlen = (strlen_t) dlsym(RTLD_NEXT, "strlen");
    printf("calling strlen.\n");
    return real_strlen(str);
}
```

在这个版本中，首先使用 `dlsym` 函数找到 `strlen` 函数的地址，由于指定了 `RTLD_NEXT` 参数，因此找到的地址一定是真正的 `strlen` 函数。另外要注意的是，引用 `dlfcn.h` 头文件之前需要定义宏 `_GNU_SOURCE`。

找到真正的 `strlen` 函数之后，使用 `printf` 打印一条记录，然后返回真正的 `strlen` 的结果。

由于这次用到了 Linux 下的动态连接器，需要在编译的时候指定 `-ldl` 选项：

``` bash
$ gcc -shared -fPIC -ldl hook.c -o hook.so
```

再次运行 `test` 程序，结果如下：

``` bash
$ LD_PRELOAD=$PWD/hook.so ./test
calling strlen.
length is 13
```

### 优化

上面的版本仍然有一个不足之处，那就是每次调用 `strlen` 的时候，都需要定位真正的 `strlen` 函数，实际上每次查找到的函数地址都是一样的。最适合的是动态库被加载的时候查找真正 `strlen` 函数的地址并存储下来，之后每次直接调用即可。

```
#define _GNU_SOURCE
#include <stdio.h>
#include <string.h>
#include <dlfcn.h>

typedef size_t (*strlen_t)(const char *str);
strlen_t real_strlen；
size_t strlen(const char *str) {
    printf("calling strlen.\n");
    return real_strlen(str);
}

void lib_init() {
    real_strlen = (strlen_t) dlsym(RTLD_NEXT, "strlen");
}
```

Linux 下的动态库文件是 ELF 格式，其中 `init` section 中的函数会在库文件加载的时候自动调用，而要让一个函数放在 `init` section 需要用 ld 的 `-init` 参数。

对于 GCC，可以通过 `-Wl` 参数指定连接器参数，编译的命令如下：

``` bash
$ gcc -shared -fPIC -ldl -Wl,-init,lib_init -o hook.so hook.c
```
