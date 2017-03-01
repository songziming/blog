title: Linux 内核中的位图
---

位图是


# GCC 内建函数

GCC 会对代码中的某些函数进行优化，例如 `memcpy` 可能会自动内联，`alloca` 会用单条汇编指令实现。这样的目的是让代码运行得更快。

如果在使用 GCC 编译时加上 `-fno-builtin`，就会禁用内建函数。如果想只禁用某些内建函数，可以使用 `-fno-builtin-function` 选项，将其中的 `function` 替换成函数名即可。需要注意的是，这里的 `function` 不能以 `__builtin_` 开头。

对应地，GCC还提供了一些函数，它们以 `__builtin_` 开头，例如 `__builtin_strcpy`。许多标准的库函数都有其对应的 `__builtin_` 版本。如果使用 `-fno-builtin` 禁用了所有的内建函数，仍然可以使用前缀为 `__builtin_` 的版本实现相应功能。

除了 C 标准库函数的 `__builtin_` 版本之外，GCC 还提供了许多额外的内建函数：

### `int __builtin_constant_p(exp)`

这个函数用来检查给定的表达式是否为编译时常亮。如果是，则 GCC 可以进行常量传播
