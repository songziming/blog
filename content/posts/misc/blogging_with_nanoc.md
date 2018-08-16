---
title: "使用 Nanoc 构建静态网站"
# kind: "article"
tags: []
---

如果把众多的静态网站生成工具比作编程语言的话，那么我感觉 Nanoc 就应该属于 C 语言。Jekyll、Hexo 等工具往往专门用于生成博客，Nanoc 与此不同，只提供最基本的功能，但应用范围也非常广泛。

静态网站的生成过程实际上就是对 markdown、liquid 等语言进行翻译，与资源文件一起生成网站资源的过程，既然只是一个编译过程，显然应用范围不仅限于博客。

在一个 Nanoc 项目下，所有的输入都放在 `content` 目录下，生成的网站则放在 `output` 目录下。生成过程的规则由 ruby 文件 `Rules` 描述。

### 关于 Ruby

个人对 ruby 并不了解，使用得也不熟练，这也是曾经一度使用 Hexo 的原因。然而 hexo 的问题太多，即使能够正常运行，也总是有几个 warning，影响使用感受。nanoc 除了使用 ruby 语言之外，其他方面感觉很成熟。

### post local assets

涉及到图片这类静态资源时，往往是把图片放在统一的资源文件夹下，然后在 markdown 文件中使用绝对路径进行引用。

其实还有一种办法，让每个文章都有自己的私有资源目录。具体来说，就是创建一个与文件名同名的目录（没有后缀），然后将资源文件放在这个目录下。markdown 文件中使用相对目录访问。

由于在生成网站的时候，每个 markdown 文件的地址自动变为 `/file_name/index.html`，因此与主文件名同名的文件夹就是翻译之后 HTML 文件所在的位置，自然也可以放入其他的资源文件。

### table of contents

为了方便浏览文章，可以让 kramdown 生成一个目录，显示在页面的左侧，用户点击目录可以迅速定位到目标位置。所以说，markdown 生成的每个标题都应该有一个 ID。

在 markdown 文件里面，可以指定 `{:toc}` 让 kramdown 生成这篇文章的目录，但如果这样的话，目录会以一个列表的形式放在文章里面，如果我们希望显示在页面的左侧，就无法实现。

如果要生成目录，首先要启用标题的ID，在 Kramdown 里面，可以通过参数 `auto_ids=true` 来实现。但 Kramdown 只认识英文字符，因此只会将标题里面的英文部分作为 ID。不知道有没有办法，让生成的标题 ID 里面包含包含中文，例如转化成拼音。

~~~
* Table of Contents
{:toc}
~~~

标记 `{:toc}` 的前面必须有一个列表，最终生成的 HTML 里面，前面那一行并不会出现。

这种方式的目录只能作为正文内容的一部分，放在文章的开头，没办法专门从文章内容里面剥离，显示在另外的部分。

毕竟 Kramdown 作为一个解析器，根本的工作就是将 markdown 转换为 html，一个输入文件到一个输出文件。如果我们想把这个目录部分从文章主体里面拿走，肯定不容易。

##### custom helper

但是 Nanoc 支持非常灵活的 helper，我们可以自己定义一个 helper，自己生成一套目录。

在博客文章页面的布局模板里面，文章正文内容是通过 `<%= yield %>` 生成的，函数 `yield()` 返回一个字符串，就是渲染之后的 HTML 内容。那么我们完全可以将 yield 的返回结果再进行一步处理。

使用 Nokogiri 解析生成的 HTML 内容，提取里面带有 id 的标题，然后将其转换为列表项。

但是仅仅这样做的话，得到的列表项只能是单级的，如果文章定义了许多不同级别的标题，则不会体现在目录里面。

# My Friends

Kang Qiao: http://kangdandan.com

<li><a href="http://wcqblog.github.io/">荒原</a></li>	
<li><a href="http://www.renfei.org/blog/">Renfei Song</a></li>	
<li><a href="http://wanzy.me/blog/">羽民</a></li>	
<li><a href="http://timmyxu.me">峯少</a></li>	
<li><a href="http://heavenduke.com">渣诚</a></li>