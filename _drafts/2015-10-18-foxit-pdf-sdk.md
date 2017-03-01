---
title: 福昕 PDF SDK 使用
category:
tags:
- PDF
- SDK
---

Foxit（福昕）PDF SDK 是一个质量很高的 PDF 工具库，去年刚刚开源的 Chrome PDF 插件就是使用福昕 PDF SDK 实现的。虽然开源的 PDF 工具库不少，但这些库往往功能不完整。福昕作为 PDF 标准的制定者之一，他们的 SDK 自然更加官方，此外，福昕是一家中国的公司！

本文主要介绍 Linux 平台下 C/C++ SDK 的使用（与 Qt 框架结合）。但 由于FoxitPDF 是一个跨平台的 SDK，其他系统上的区别很小。

FoxitPDF 不是一个开源软件，因此要使用必须在福昕官网申请试用（可以选择个人无时限试用）。下载并解压之后，会发现其中提供了对应平台的动态链接库（位于 `lib` 目录下，有 32 位和 64 位两个版本），和开发需要的头文件（位于 `lib` 目录下）。`lib` 目录下还有两个证书文件，这两个文件的内容是激活 SDK 功能所需要的。

FoxitPDF 以动态链接库的形式提供，开发者只需要设置头文件的引用路径，并添加动态链接库的引用即可。

### FoxitPDF SDK 初始化与退出


程序启动时，需要首先初始化 FoxitPDF SDK Manager，只有初始化完成，才能够使用其他 SDK 中的函数。初始化方法如下：

``` c
FS_RESULT ret = FSCRT_Library_CreateDefaultMgr();
if (FSCRT_ERRCODE_SUCCESS != ret) {
    qDebug() << "Cannot initialize library manager";
}
```

函数 `FSCRT_Library_CreateDefaultMgr` 必须是应用程序所调用的第一个 FoxitPDF SDK 函数，如果该函数的返回值为 `FSCRT_ERRCODE_SUCCESS`，说明初始化成功。

对应地，当程序退出时，需要清除 FoxitPDF SDK Manager 以释放资源，方法如下：

``` c
FSCRT_Library_DestroyMgr();
```

### 激活 FoxitPDF SDK

FoxitPDF 是一个商业软件，需要使用证书激活才能使用全部功能。在 `lib` 目录下，包含了 `gsdk_key.txt` 和 `gsdk_sn.txt` 两个文件。这两个文件包含了激活 SDK 所需的信息。激活 SDK 的代码如下：

``` c
const char *sn = "<gsdk_sn.txt 文件中 “SN=” 之后的内容>";
const char *key = "<gsdk_key.txt 文件中 “Sign=” 之后的内容>";

FSCRT_BSTR licenseId;
FSCRT_BStr_Init(&licenseId);
FSCRT_BStr_Set(&licenseId, sn, strlen(sn));

FSCRT_BSTR unlockCode;
FSCRT_BStr_Init(&unlockCode);
FSCRT_BStr_Set(&unlockCode, key, strlen(key));

FSCRT_License_UnlockLibrary(&licenseId, &unlockCode);

FSCRT_BStr_Clear(&licenseId);
FSCRT_BStr_Clear(&unlockCode);
```

代码似乎不少，关键的只有 `FSCRT_License_UnlockLibrary` 一个函数，这个函数接受 licenseId 和 unlockCode 作为参数，根据 License 的类型解锁 SDK 的功能。licenseId 和 unlockCode 都是字符串，但 FoxitSDK 使用的是自己的 `FSCRT_BSTR` 类型，函数 `FSCRT_BStr_Init` 用来创建 `FSCRT_BSTR` 对象，函数 `FSCRT_BStr_Set` 用来给对象赋值，函数 `FSCRT_BStr_Clear` 用来清除对象，释放空间。

实际上，对于字符串常量，还可以用如下两种方式方便地创建对象：

``` c
FSCRT_BSTRC(myString, "The content of string");
FSCRT_BSTR myString = FSCRT_BSTRD("The content of string");
```

由于字符串常亮的数据保存在可执行文件只读数据段中（`.rodata`），并不需要释放内存，因此可以直接使用上面的两个宏创建 `FSCRT_BSTR` 结构体。

### API 风格

我感觉，FoxitPDF SDK 具有典型的 WIN32 风格，个人并不是很喜欢，但是这种风格在 FoxitPDF SDK 中还是很统一的。

首先，SDK 提供的是 C 风格的接口，定义有大量的函数和结构体。所有函数和结构体的名称都有前缀 `FSCRT` 或 `FSPDF`，函数的返回值为状态码，表示函数执行成功或是失败，输入和输出都通过参数实现。在前面的例子中，函数 `FSCRT_Bstr_Init` 用来创建一个 `FSCRT_BSTR` 类型的对象，但是新创建的对象并不是通过返回值返回，而是通过指针类型的参数回传。

### 模块

整个 FoxitPDF SDK 分为若干模块，例如 PDF、Barcode 等，需要使用某个模块的功能，同样需要在程序启动和退出时启用和析构模块。例如，PDF 模块的初始化和析构的方法如下：

``` c
FSCRT_PDFModule_Initialize();
FSCRT_PDFModule_Finalize();
```

### 渲染局部页面

渲染 PDF 页面的局部可以显著地提高程序效率。局部渲染的关键就是 PDF 页面大小大于显示区域。用到的两个 API 函数：
- `FSPDF_Page_GetMatrix`
- `FSPDF_RenderContext_SetMatrix`

假设正常的显示区域宽为 `w`，高为 `h`，正常使用方式为：

``` c
FS_RESULT ret = FSPDF_Page_GetMatrix(page, 0, 0, w, h, 0, &matrix);
```

这样，相当于创建了一个二维变换矩阵，将原 PDF 页面的二维空间映射到 `w*h` 的二维空间。

如果使用下面的方式调用函数：

``` c
FS_RESULT ret = FSPDF_Page_GetMatrix(page, 0, 0, w * 2, h * 2, 0, &matrix);
```

这样将页面映射到 4 倍大小的空间。而 Bitmap 的大小还没有变，这样就相当于将页面放大了 4 倍，并且只显示左上角 1/4 的部分。

如果希望显示的区域不位于左上角，则可以修改 `FSPDF_Page_GetMatrix` 中的两个 `0`，这两个参数表示 PDF 文件的左上角将会位于显示设备的哪个坐标之上。

### 关于坐标

PDF 页面坐标的原点在左下角，显示设备（如位图）坐标的原点在左上角。
