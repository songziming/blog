---
title: Android平台系统架构
layout: page
---

![](/assets/images/android_arch.jpg)

课件 Part I:

- [Chapter 1 Introduction](http://songziming.qiniudn.com/arch/chapter1_Introduction.pdf)
- [Chapter 2 Modeling](http://songziming.qiniudn.com/chapter%202%20modeling.pdf)
- [Chapter 4 Android Platform Review](http://songziming.qiniudn.com/chapter%204%20android%20platform%20overview.pdf)
- [Chapter 5 Android Application Model](http://songziming.qiniudn.com/chapter%205%20android%20application%20model.pdf)
- [Chapter 6 Android Internals](http://songziming.qiniudn.com/chapter%206%20Android%20Internals.pdf)
- [Chapter 7 Android Binder IPC](http://songziming.qiniudn.com/Chapter%207%20android-binder-ipc.pdf)

Part II:

- [第03章 质量属性](http://songziming.qiniudn.com/%E7%AC%AC03%E7%AB%A0%20%E8%B4%A8%E9%87%8F%E5%B1%9E%E6%80%A7.pdf)
- [第04章0 数据流风格](http://songziming.qiniudn.com/%E7%AC%AC04%E7%AB%A00%20%E6%95%B0%E6%8D%AE%E6%B5%81%E9%A3%8E%E6%A0%BC.pdf)
- [第04章1 数据流风格案例](http://songziming.qiniudn.com/%E7%AC%AC04%E7%AB%A01%20%E6%95%B0%E6%8D%AE%E6%B5%81%E9%A3%8E%E6%A0%BC%E6%A1%88%E4%BE%8B.pdf)
- [第04章2 调用返回风格](http://songziming.qiniudn.com/%E7%AC%AC04%E7%AB%A02%20%E8%B0%83%E7%94%A8%E8%BF%94%E5%9B%9E%E9%A3%8E%E6%A0%BC.pdf)
- [第04章3 独立构件体系结构](http://songziming.qiniudn.com/%E7%AC%AC04%E7%AB%A03%20%E7%8B%AC%E7%AB%8B%E6%9E%84%E4%BB%B6%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84.pdf)
- [第04章4 虚拟机解释器体系结构](http://songziming.qiniudn.com/%E7%AC%AC04%E7%AB%A04%20%E8%99%9A%E6%8B%9F%E6%9C%BA%E8%A7%A3%E9%87%8A%E5%99%A8%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84.pdf)
- [第04章5 以数据为中心的仓库体系结构](http://songziming.qiniudn.com/%E7%AC%AC04%E7%AB%A05%20%E4%BB%A5%E6%95%B0%E6%8D%AE%E4%B8%BA%E4%B8%AD%E5%BF%83%E7%9A%84%E4%BB%93%E5%BA%93%E4%BD%93%E7%B3%BB%E7%BB%93%E6%9E%84.pdf)


报名或者修改自己的选题，发送邮件到`s.ziming@hotmail.com`。

决定题目之前请确认该话题未占用。

我不一定会立即回复，但是会根据收到邮件的顺序更新下表。

P.S. 不一定要选机器学习相关的，只要找个有规模的软件，分析一下它的架构即可。

> 选题的时候，注意不要选“库”，最好选择一个“平台”或“框架”。所谓“库”，是指那些不会自己主动运行，而是由使用库的程序调用的代码和数据。“平台”和“框架”，是指那些能够主动运行，为上层的应用提供平台抽象和封装的软件。例如Java和.Net的虚拟机，就属于“平台”的范畴，因为它们建立在操作系统之上，为上层代码提供运行环境。
>
> 老师的原话为：
>
> > 大家报的系统，要求必须有运行时系统，不能拿个算法库分析。

<!-- 一人展示，其余两人负责回答问题 -->

|  # |         人员         |      选题      |
|:--:|:--------------------:|:--------------:|
|  1 | 宋子明/王剑锋/朱公朴 |   Kubernetes   |
|  2 | 刘家辉/林彤伟/刘鹏   |   Docker       |
|  3 | 元日升/李庚婉/张建光 |   ROS          |
|  4 | 余红松/俞晋/李洪旭   |   Theano       |
|  5 | 高远/刘永刚/邵帅     |   Kafka        |
|  6 | 王玉世/吴志新/董文轩 |   MXNet        |
|  7 | 李佳骏/胡绍宇/姬文辉 |   Spark        |
|  8 | 孙尧佳/石圣东/田辞   |   HBase        |
|  9 | 尹瑞鹏/白俊华/李静   |   CloudStack   |
| 10 | 王博文/王永朋/张侃   |   HDFS         |
| 11 | 彭楚风/王晨/燕星宇   |   Ambari       |
| 12 | 朱鸿基/马欣欣/付宁   |   OpenStack    |
| 13 | 孙俊萍/宋宁/陈姝君   |   Hadoop       |
| 14 | 池轩/王一名/田君     |   KVM          |
| 15 | 林泉沛/石浩卿/黄曦   |   Ceph         |
| 16 | 彭然/何航宇/张爱松   |   Storm        |
| 17 | 张沛/张一鸣/周程健   |   Mesos        |
| 18 | 杨婧玥/王洁薇/魏星   |   Redis        |
| 19 |                      |                |
| 20 |                      |                |
| 21 |                      |                |
| 22 |                      |                |
| 23 |                      |                |
| 24 |                      |                |
| 25 |                      |                |
| 26 |                      |                |
| 27 |                      |                |
| 28 |                      |                |
| 29 |                      |                |
