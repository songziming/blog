尝试开发一种新的静态网站生成器

网站生成器实际上没那么复杂，只需要：
1. 收集 post、page
2. 分析 post、page 里面的元数据，渲染 markdown，同时引用静态资源文件（图片）
3. 根据页面元数据，自动生成目录。包括按时间汇总的线性列表，还有按话题、标签分组

在这个过程中，我们还可以做一些特殊处理：
1. 使用 [pangu.py](https://github.com/vinta/pangu.py) 处理 markdown 文本，确保中英文之间加入空格
2. 使用引用计数统计每个静态资源使用多少次，不再使用的静态文件提醒作者删除
3. 检查内部链接的正确性，允许使用相对路径引用别的页面，自动转换为正确的 url
4. 允许在文本中内嵌代码，代码不是显示出来，而是 render 过程中执行，可以自动生成图表
5. 使用 Pandoc 渲染 markdown，这样能进一步扩展样式

### 技术方案

选择比较熟悉的 Python 作为开发语言，使用 Pandoc 渲染 markdown，允许在文章里内嵌 matplotlib 图表。

还可以使用 jupyter notebook，将其转换成 html，这样可以直接在 vscode 内部看到渲染出来的样子。

至于模板引擎，我们选择 Jinja2，将正文放入页面框架中，添加 header、footer 还有侧边目录。

### 安装依赖项

Pandoc 是 Haskell 开发的库和工具，可以使用 conda 安装：

~~~
conda install -c conda-forge pandoc
~~~

然后再安装 pandoc python 模块：

~~~
pip install -U pandoc
~~~

其他依赖项：

~~~
pip install -U pangu    # 自动添加中英文空格
pip install -U jinja2   # 模板引擎
~~~

### 解析 frontmatter

所谓 frontmatter 就是 markdown 开头的 yaml 元数据，多数静态网张都需要这个。

因为 frontmatter 的存在，markdown 不再是单纯的 markdown，不能直接交给 pandoc 解析。

其他 SSG 是怎么做的？特别是哪些 Python 开发的工具，如 MkDocs、Pelican。它们的办法很原始，读取 markdown 文本，手工分割为两部分。

但是我们有更好的选择，Pandoc 原生支持 yaml-metadata，甚至允许在 markdown 中间任意位置


### 使用 Python 解析 markdown 并提取元数据

pandoc 是独立的命令行工具，可以使用 subprocess 调用。但是，转换为 html5 没有问题，但这会丢失元数据。

正好，pelican 有第三方的 pandoc-reader，我们可以看看这个开源项目的源码，搞懂它们如何获取元数据。

pandoc 生成网页的时候，可以指定 template。模板内容为：

~~~
$meta-json$
<body>
$if(toc)$
<nav id="$idprefix$TOC" role="doc-toc">
$if(toc-title)$
<h2 id="$idprefix$toc-title">$toc-title$</h2>
$endif$
$table-of-contents$
</nav>
$endif$
$body$
$for(include-after)$
$include-after$
$endfor$
</body>
~~~

转换文档的命令：

~~~
pandoc -f markdown -t html5 --template=template.html
~~~

注意模板开头有json格式的元数据，输出文件里包括json和html两部分，混合在一起。但是，meta-json一定只占据一行，因此在Python代码中，使用partition函数提取第一行即可。

### 利用pandoc模板？

理论上，markdown转换为html片段，只输出正文部分，而不是一个完整的HTML页面。body以外的部分由我们自己配置，这就是 jinja2 模板引擎的任务。

pandoc提供了模板功能，jinja2也有模板功能，使用哪一种？

jinja2 更合理，因为渲染用的数据是Python代码设置的，说明这些数据还能用于别处。除了渲染单独页面，生成首页、目录页等特殊页面也需要这些信息。

### 总结：从pandoc获取AST

借助template和variables，将我们需要的信息直接写入生成的html片段。

直接分析AST？可以用 `-t native` 或 `-t json` 生成抽象语法树，但是解析工作还要我们进行。而且这就要求同一个markdown至少转换两次，一次获得AST，另一次转换为html。

AST是有必要的，因为还要获取一篇文章内部的目录。可以用模板中的 `$toc$` 生成目录，但这样的目录直接是 html 格式，无法进一步定制。

还可以使用 beautifulsoup 解析生成的 html，

### 使用 python 开发 pandoc-filter

filter 可以实现自定义 block 类型，例如内嵌 graphviz、tikz

什么是 filters？filter 是文档 AST 的过滤器，输入 AST，输出修改后的 AST。整体文档转换流程就是：

~~~
INPUT --reader--> AST --filter--> AST --writer--> OUTPUT
~~~

开发 filter 有两种方案：
- lua filters，使用 pandoc 内置的虚拟机解释运行，速度较快，但只能使用 lua
- JSON filters，输入输出的 AST 均为 JSON 格式，任何语言都可以，使用标准输入输出

调用 json filter，直接用 pipe 将三个指令连起来：

~~~
pandoc -f markdown -t json source.md | \
    ./my_filter | \
    pandoc -f json -t html5 -o output.html
~~~

还可以使用命令行参数 --filter，效果和前一种方法一样：

~~~
pandoc -f markdown -t html5 --filter ./my_filter source.md -o output.html
~~~

手写filter当然是可以的，但使用 pandocfilters 模块提供的辅助函数会更方便。

~~~py
from pandocfilters import toJSONFilter

def processNode(key, value, format, meta):
    if key=='Header':
        print(f'header level {value[0]}, content {value[2]}')
~~~