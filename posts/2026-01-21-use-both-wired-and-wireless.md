---
title: Windows同时使用有线和无线网络
tags:
  - network
  - tips
---

笔记本有两个网卡，一个有线，一个无线。如果同时连接有线和无线，默认所有流量都会走有线。如果希望某些地址通过无线访问，则需要配置路由表。

运行 `ipconfig /all` 获取有线和无线适配器的默认网关（而不是IP），假设有线网关是 44.44.44.44，无线网关是 55.55.55.55。

运行 `route print` 打印路由表，注意开头的接口列表，得到无线网卡的接口号。例如下面的输出就表示，无线网卡接口编号是 2：

~~~
 24...00 ff 7c 7a f3 5f ......DACS VNIC
 33...........................Wintun Userspace Tunnel
 21...7c 8a e1 a0 93 06 ......Realtek PCIe GbE Family Controller
 26...80 b6 55 68 c3 e8 ......Microsoft Wi-Fi Direct Virtual Adapter
 15...82 b6 55 68 c3 e7 ......Microsoft Wi-Fi Direct Virtual Adapter #2
 31...00 09 0f fe 00 01 ......Fortinet Virtual Ethernet Adapter (NDIS 6.30)
  2...80 b6 55 68 c3 e7 ......Intel(R) Wireless-AC 9560
 22...00 ff 73 44 e1 1a ......Sangfor SSL VPN CS Support System VNIC
 14...80 b6 55 68 c3 eb ......Bluetooth Device (Personal Area Network)
  1...........................Software Loopback Interface 1
~~~

假设我们希望通过无线访问 123.4.5.*，其他的网络都通过有线访问（默认），只需要针对 123.4.5.* 添加一个路由规则：

~~~cmd
route add -p 123.4.5.0 mask 255.255.255.0 55.55.55.55 metric 2 if 2
~~~

metric 表示跃点数，取值越小表示优先级越高。添加路由规则后，访问 123.4.5.* 的数据包就会发送给 55.55.55.55，即无线网络的网关。

> 只要一个设备接入两个网络，它就是一个路由器（此路由器不是无线路由器）。Windows 也有路由功能，只是一般只接入一个网络，因此路由功能不常使用。
>
> 路由表分为静态路由表和动态路由表两部分，我们添加的是静态路由，动态路由表是根据路由算法自动更新的。