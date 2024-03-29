---
title: Git 解惑
draft: true
---


# 重新理解“管理版本”

有些思想不仅适用于 git，也适用所有版本管理。

## 土法版本管理：一天一个压缩包

每天下班之前，将所有人开发的代码汇总起来，把整个代码仓库打包成压缩文件，按日期命名。一段时间后，我们就有了一堆压缩包。

如果有一天，某人不小心开发了一个 BUG，实在难以修复，就可以将前一天的压缩包展开，重新在前一天的状态之上开发。

这种土法版本管理方案的优缺点如下：

- 优点
    1. 无需软件，逻辑简单，上手容易
- 缺点
    1. 不够精细，一天只有一个状态
    2. 改动不清晰，无法直接看出两个版本之间有哪些改动，只能额外用文档
    3. 数据冗余，相邻两个状态大部分内容是相同的，但只能保存多份

土法版本管理除了简单，剩下全是缺点。下面介绍 git 是如何针对性地解决上述缺点的。

每天创建的压缩包，就相当于commit，表示一个状态。

## tarball and patches

Linus 曾说过，早期 Linux 协作开发的版本控制方法就是 tarballs and patches，即压缩包配合差异文件。

有点类似于现在的 APP 增量更新，只需要发送修改的部分，也就是 patch 文件。

这仍然属于手动版本管理，而且要注意 patch 和 tarball 的对应关系。

问题在于，记录状态的一直是 tarball，patch 仅仅用在开发者间同步。多人一同开发，必须以某个人（linus）的版本为准。

## 中心式版本管理

这是为了解决团队开发的问题，每个开发者登录到服务器上，不是修改本地文件，而是直接在服务器上编辑源代码。

受限于网络，完全远程编码可能不方便，因此这类工具可以 checkout 一部分文件到本地，修改测试之后提交。

## git 如何解决上述缺点

### 使用 commit 提升精细度

在git里面，有个关键概念是commit，类似于每天打包的压缩文件。

commit代表一个状态，记录当前状态的内容。用户可以随意创建commit



# Git 相关概念

## commit、分支有什么关系

commit 代表一个状态。

commit 可以有前驱，指向另一个 commit。初始 commit 没有前驱，merge commit 有两个前驱，普通 commit 有一个前驱。

分支是一个指针，指向某个 commit，表示该分支所处的状态。

## 理解 HEAD 指针

HEAD 指针表示当前状态，

## 本地和远程

git 是分布式版本管理方案，何为分布式？就是每个仓库都是独立的，相互不依赖。

本地仓库和远程仓库是两个完全不同的仓库，只是里面保存的代码、commit历史“恰好”相同。





# 常见问题

## 为什么 commit 之前需要 add

这样才能挑选一部分修改的文件提交

## 误操作切换到了某个 commit，如何回退

使用 `git reflog` 查看