---
title: "Linux 内核构建系统"
category: "开发"
tags: ["linux"]
---

Linux 内核可以用于许多不同系统，从嵌入式设备到超级计算机，都可以通过同样的源代码编译而成。而且 Linux 内核最终编译出来的不仅是内核的镜像，也包括一系列模块。总之，在 Linux 内核的构建过程中，隐藏着大量的黑魔法。

构建系统的作用就是，决定哪部分代码将用于编译，以及如何编译。Linux 中，这部分称作 KBuild（Kernel Build System）。

### KBuild

关于 KBuild，更详细的文档见 `Documentation/kbuild`
