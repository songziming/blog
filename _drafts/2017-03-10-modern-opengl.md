---
title: 现代OpenGL
category: "开发"
---

想玩 OpenGL 也不是一天两天了，大一选过一个 OpenGL 的选修课，虽然教的是 1.0 版本的 OpenGL，但是对管线等概念有了基本的印象。

所谓现代 OpenGL，是一种笼统的程序，一般指 3.0 以后，有了 Core Profile 的 OpenGL。相比于之前的版本，有了着色器程序 Shader，有了可编程管线。虽然实际编程中未必会用到这些高端的东西，但了解一下总无妨。

### SDL & GLEW

OpenGL 的底层由各个显卡驱动实现，在不同平台上没有统一的使用方法。使用 SDL 和 GLEW 是相对容易的方法。

### Vertex Array Object (VAO)

跟着教程学的时候，文档上说，需要创建一个 VAO，但没有过多解释为什么。VAO 用下面的方法创建并绑定：

```
GLuint vao;
glGenVertexArray(1, &vao);
glBindVertexArray(vao);
```

OpenGL 的一大特色就是，不管什么东西，都是一个 uint 类型的 ID，所有操作都用这个 ID，而真正的对象被驱动隐藏了起来。此外，VAO 可以创建很多个，但是同一时刻只能有一个 VAO 处于活动状态，即绑定状态。如果我们要对一个 VAO 进行某些操作，不是调用类似 `glSomeOperation(vao, ...)` 的函数，而是首先用 `glBindVertexArray` 绑定 VAO，然后调用函数进行操作。执行操作的函数并没有接受 vao 作为参数，因为默认操作的就是全局的 VAO。

个人理解，VAO 就像一个状态机。都说 OpenGL 是一个状态机，其实这些状态都是存在 VAO 中的。所以一些简单的 OpenGL 程序只需要创建一个 VAO 并绑定就再也不用关心了，好像这东西没有任何用一样。

### Vertex Shader & Fragment Shader

简要描述一下 OpenGL 绘制图像的过程。OpenGL 能够绘制的基本图元只有三角形，但是一次 draw call 可以绘制一系列的三角形。这个“绘制”是通过 Vertex Shader 完成的，所谓 Shader 就是在 GPU 上执行的程序，Vertex Shader 运行的输出就是一串三维点的坐标。

可以把显示器当作一个标准立方体，XYZ 轴的范围都是 $[-1,1]$，Vertex Shader 输出的点，就是在这个空间坐标系之内的（称作屏幕坐标系）。如果直接在这种空间内绘画，显然不容易做出立体效果，因此 Vertex Shader 会通过各种矩阵变换（通常是模型-视图-投影矩阵），将原始坐标转换到屏幕坐标系。要显示的立体模型可能很复杂，包含非常多的点（Vertex），而这每个 Vertex 都要经过 Shader 进行矩阵变换。好在所有 Vertex 所进行的变换都是等价的，所执行的程序完全相同，只是数据不同，典型的 SIMD 模型。恰好 GPU 非常适合做这种事（应该说，为了做好这种事，GPU 才做成了这种样子），因此在 Vertex Shader 之后，得到了屏幕坐标系之下，模型的点的坐标。

Vertex Shader 的输入是一个 Buffer，里面是模型的点在原始空间下的坐标。输出也是 Buffer，包含了屏幕坐标系之下的坐标。

有了坐标还不够，还需要知道每个点要显示的颜色。最终显示在屏幕上的颜色不仅反映了模型的材质，还与光照、反射、阴影等高级话题有关。为了实现多种复杂的图形效果，颜色也由专门的 Shader 来计算，这就是 Fragment Shader。

### 贴图

贴图决定了在屏幕上显示的像素的颜色，因此贴图的细节是在 Fragment Shader 中决定的。GLSL 中有一个内置函数 `texture`，能够根据贴图采样得到目标颜色。
