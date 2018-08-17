---
title: "使用 Nanoc 构建静态网站"
# kind: "article"
tags: ["nanoc", "blog"]
---

算起来，这应该是我第二次折腾 Nanoc 了。上一次使用 Nanoc，就给我留下了很好的印象，虽然核心功能不多，但是构建过程非常直接，而且可定制程度非常高。印象中，上一次使用 Nanoc，甚至编写了一个 helper，实现 Pandoc 渲染和内嵌 TikZ 绘图。但是由于 Ruby 的环境不方便在 Windows 下面运行，所以就放弃了。

不过这回有了 WSL，环境就不再是问题，于是重新捡起 Nanoc。

### 基本结构

Nanoc 最大的特点就是简单，同时还有很强的扩展性。`content` 目录下的所有文件都是输入，每个文件都称作一个 item。构建静态网站的过程，就是对所有的 item 执行对应的处理流程。各个 item 的构建规则由 `Rules` 文件描述，输出的文件就放在 `output` 目录下。

Nanoc 不区分源文件的类型，无论 html、markdown、css 还是图片，只要放在 `content` 里面，就属于 item。因此在规则文件 `Rules` 中，我们可以根据 item 的文件名来分类，进行执行不同的编译规则。从源文件到最终的静态网站，构建过程的每个步骤都是清晰明确的。

### 自动生成目录

为了方便浏览文章，可以在渲染 markdown 的时候，自动生成一个目录，显示在页面的左侧，用户点击目录可以迅速定位到目标位置。

如果要生成目录，首先要启用标题的 ID，这样我们才能生成链接，指向对应的标题。在 Kramdown 里面，可以通过指定参数 `auto_ids=true`，让生成的每一个标题都带有 id 属性。

生成了标题 ID 之后，在 markdown 文件里面，就可以用 `{:toc}` 指定 kramdown 生成这篇文章的目录，目录就放在标记的位置：

~~~ md
* Table of Contents
{:toc}
~~~

标记 `{:toc}` 的前面必须有一个列表，最终生成的 HTML 里面，前面那一行并不会出现。

但是，这种方式生成的目录只能作为正文内容的一部分，放在文章的开头，没办法专门从文章内容里面剥离，显示在另外的部分。毕竟 Kramdown 作为一个解析器，根本的工作就是将 markdown 转换为 html，说白了就是一个输入文件到一个输出文件，不能产生两个输出文件。

### 自定义 helper 生成目录

既然 Kramdown 自带的功能不满足我们要求，那就利用 Nanoc 灵活的扩展能力自己开发。

生成目录其实非常简单，将翻译之后的 HTML 片段进行分析，提取里面所有的标题（`h1` 到 `h6`），获取每一个标题的内容和 id，将内容重新组合为列表项。

~~~
Input:  <h3 id="section">My Header</h3>
Output: <a href="#section">My Header</a>
~~~

使用 Ruby 语言解析 HTML，可以用到 Nokogiri，代码如下：

~~~ ruby
doc = Nokogiri::HTML::DocumentFragment.parse(html)
sel = (1..6).map(&-> (x) { "h#{x}[@id]" }).join("|")
doc.xpath(sel).map { |h|
    "<li><p><a href=\"##{h[:id]}\">#{h.children}</a></p></li>"
}.join
~~~

这几行代码，就可以选出所有标题，并生成一组列表项，前后再加上 `<ul>` 和 `</ul>`，就是一个完整的列表。

当然，这样的列表丢失了标题的级别，显示出来都成了平级的。最终的代码可以参考 Github。

### sticky sidebar

我们将文章的目录显示在页面的左侧，但是，如果让左侧的目录随着正文一起滚动，那么如果滚到文章后面，目录就会完全看不到，如果用户希望使用目录进行导航，就还要回到页面的开头。显然这非常不方便，最好能让目录一直显示在页面的左侧。

网上查了一番，发现有一个 CSS 属性 `position: sticky`，似乎能解决我这个需求。然而试验了之后，发现这个属性的问题非常多。它只会和父元素的边界进行比较，从而决定自己应该是 relative 还是 fixed，但在我们的页面中，左侧的目录是放在一个容器 div 内部的，这就导致 `position: sticky` 属性没有效果。

最后，还是使用最传统的 JS 方法。所谓 sticky sidebar，就是一开始目录随着页面一起滚动，当目录就要碰到 viewport 顶端的时候，变为 fixed 模式，固定在 viewport 中当前的位置。当滚动到页面底端，又要和 footer 碰撞的时候，再变为 absolute 布局，紧贴外层 div 的下边界。

所以，主要的逻辑就是计算出两个状态转换的关键节点，然后不断检查页面滚动的事件，如果发现越过了这两个节点，那就通过修改 class 属性，调整侧边目录的显示效果。

### My Friends

<!-- - [康乔](http://kangdandan.com) -->

- [荒原](http://wcqblog.github.io)
- [Renfei Song](http://www.renfei.org/blog)
- [羽民](http://wanzy.me/blog)
- [峯少](http://timmyxu.me)
- [渣诚](http://heavenduke.com)