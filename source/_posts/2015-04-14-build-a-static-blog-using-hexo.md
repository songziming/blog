---
title: "使用 Hexo 构建静态博客"
category: "工具"
tags: ["hexo", "node.js"]
---

静态博客有许多好处，其中最核心的一点就是轻便。省去了后端和数据库，只有最基本的静态 HTML 文件，全部由静态博客生成器负责创建。

Hexo 是一个 Node.js 编写的静态博客生成器。这些生成器往往采用现有的 Web 框架，但不是在收到 HTTP 请求的时候渲染页面，而是在执行生成的时候就把所有 Markdown 格式的源文件转换为 HTML。Hexo 支持 EJS、Handlebars、Jade 这些流行的模板引擎，因此编写博客样式非常方便。

使用 Hexo 并不困难，但是定制一个顺眼的主题就比较费劲了。对于博客来说，一个主题起码应该具备以下的支持：

表格

| A | B |
|:-:|:-:|
| 1 | 2 |
| 3 | 4 |
| 5 | 6 |
| 7 | 8 |
| 9 | 0 |

代码块，能够对不同语言进行着色

``` python
def func():
	pass
```

数学公式，质能转换

$$ E=MC^2 $$

麦克斯韦方程组，注意在 Markdown 中，换行要用四个连续的反斜线

$$ \nabla \times \vec{\mathbf{B}} -\, \frac1c\, \frac{\partial\vec{\mathbf{E}}}{\partial t} = \frac{4\pi}{c}\vec{\mathbf{j}} \\\\
\nabla \cdot \vec{\mathbf{E}} = 4 \pi \rho \\\\
\nabla \times \vec{\mathbf{E}}\, +\, \frac1c\, \frac{\partial\vec{\mathbf{B}}}{\partial t} = \vec{\mathbf{0}} \\\\
\nabla \cdot \vec{\mathbf{B}} = 0 $$

以及引用

> 这是一般的引用

但是，注意引用内部也可能有其他的格式

> # 引用中也可以有标题
>
> 引用中的**段落**和公式$\sum_{i=1}^\inf i = -\frac{1}{12}$
>
> > 引用中的**引用**
> > > 引用中的引用中的引用
>
> | X | Y |
> |:-:|:-:|
> | a | b |
> | c | d |

更有甚者

> 引用
> > 引用中的引用
> > > 引用中的引用中的引用
> > > > (引用中的)^3 引用

下面是 Hexo 的基本使用方法。

- - -

### Create a new post

``` bash
$ hexo new "My New Post"
```

More info: [Writing](http://hexo.io/docs/writing.html)

### Run server

``` bash
$ hexo server
```

More info: [Server](http://hexo.io/docs/server.html)

### Generate static files

``` bash
$ hexo generate
```

More info: [Generating](http://hexo.io/docs/generating.html)

### Deploy to remote sites

``` bash
$ hexo deploy
```

More info: [Deployment](http://hexo.io/docs/deployment.html)

### Code highlight

``` cpp
#include <iostream>
using namespace std;

int main(int argc, const char *argv[]) {
	cout << "Hello, world!" << endl;
	return 0;
}
```
