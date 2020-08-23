---
title: GCC+Makefile管理依赖关系
date: 2018-08-16
---

## 问题描述

Make可以实现增量编译，然而这需要在Makefile中指定每个源文件的依赖关系：

``` makefile
sample.o: sample.c header1.h header2.h
    CC -c -o $@ $<
```

这里面，`header1.h`和`header2.h`便是`sample.c`所需的头文件，如果`header1.h`改了，Make就能根据这条规则自动判断出，`sample.c`需要重新编译。

但是，这种方式需要在Makefile中显式写出引用了哪些头文件，每当`sample.c`增加或删去了一个头文件的引用，还需要更改Makefile。如果项目规模比较大，头文件之间还会相互引用，这是将会是一件非常痛苦的事情。

## 自动生成依赖关系

幸好，GCC（以及Clang）提供了自动生成依赖关系的功能，而且生成的依赖关系可以直接用在Makefile中。

最简单的方法是使用参数`-MM`，在上面的例子中，使用命令`gcc -MM sample.c`就可以在终端内输出依赖列表：

```
sample.o: sample.c header1.h header2.h
```

可以看到，输出格式正是Makefie需要的，完全可以把这个命令的输出结果直接复制到Makefile中去。

其实生成依赖列表还有一个参数`-M`，但是`-M`会把所有头文件输出，包括`stdio.h`这类的系统标准头文件，而`-MM`则会忽略这些标准头文件。由于在实际项目中，只有自定义头文件才会修改，因此`-MM`更加合适。

默认情况下，使用`-M`或`-MM`生成的规则的目标名就是源文件明，将后缀替换为`.o`，如果希望使用其他的目标名，可以增加一个`-MT`参数，例如：

``` sh
gcc -MM -MT target.o sample.c
```

输出为：

```
target.o: sample.c header1.h header2.h
```

还有两个参数，`-MD`和`-MMD`，它们会让GCC在编译程序的同时生成依赖列表，并保存成文件。默认的文件名就是规则的目标，将后缀替换成`.d`，如果要指定生成的文件名，可以使用参数`-MF`。

还有一个非常有用的参数是`-MP`，它会给每个依赖的头文件生成一条规则，内容为空，就像这样：

``` sh
gcc -MM -MP -MT target.o sample.c
```

输出为：

```
target.o: sample.c header1.h header2.h

header1.h:

header2.h:
```

生成这些多余的规则是非常有用的，如果删除了某些头文件而没有更新Makefile，这些空规则可以避免因找不到头文件而报错退出。

## 自动化

用上面介绍的这些参数，能够自动生成依赖规则，但是仍然需要对每一个文件单独执行一遍。然而，若能和Make的模糊匹配结合起来，就可以实现真正的自动化管理。

GNU Make 支持规则的正则表达式匹配，例如：

``` makefile
%.o: %.c
    CC -c -o $@ $<
```

可以匹配所有`.c`文件生成`.o`文件的规则。如果在编译命令中加上`-MMD`参数，就能在编译的同时生成依赖列表文件：

``` makefile
%.o: %.c
    CC -c -MT $@ -MMD -MP -MF $*.d -o $@ $<
```

这样，在编译的同时，就会生成后缀名是`.d`的依赖文件。在Makefile文件末尾，可以用`include`命令包含这些依赖列表文件：

``` makefile
-include $(patsubst %, %.d, $(basename $(sources)))
```

其中变量`$(sources)`是全部的源文件，`patsubst`函数的作用是将所有的源文件后缀名换成`.d`，于是就成了刚刚生成的依赖列表文件。在`include`命令前加一个减号，可以避免找不到某个文件而报错。

用这种方法，执行Make的时候会自动寻找依赖文件，如果没有就会在编译的同时生成依赖文件。如果找到了依赖列表文件，就会自动包含在Makefile中。

> 参考：[Auto-Dependency Generation](http://make.mad-scientist.net/papers/advanced-auto-dependency-generation/)