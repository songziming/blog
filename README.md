自己开发的静态网站框架，使用 Python + Pandoc + Jinja2。

满足本站需求即可，不必对标 Pelican、MkDocs 等成熟项目。

# 安装依赖项

~~~
conda install -c conda-forge pandoc
npm install -g csso-cli
pip install -U pypinyin pandocfilters Pygments Jinja2 htmlmin
~~~

# 构建静态网站

~~~
python make.py
python -m http.server -d output
~~~

# 为什么自己定制一个生成器

为了满足一些个性化需求：
- 使用 Python，自己很熟悉
- 使用 Pandoc 解析 markdown，支持很多扩展格式（如定义列表）、支持自定义 filter（实现内嵌 tikz 等功能）
- 方便增加自定义功能，如中文转拼音，中英文间隔，标题自动编号，资源文件引用计数
- 检查文章格式合法性，例如相邻 header 不允许跨级，引用的目标文件必须存在

# 网站构建的大致流程

1. 收集源文件
2. 分析每个源文件，包括：
   1. 从源文件路径和文件名中获取分类、发表日期、链接地址三个信息
   2. 从源文件内容中分析 yaml 元数据，提取其他信息（标题、关键词、是否显示目录、是否隐藏）
   3. 解析 markdown，转换为 AST
3. 对文章列表和每个文章进行修改：
   1. 筛选出不隐藏的文章（去掉 draft）
   2. 检查是否存在网址冲突，即两篇文章拥有相同的目标地址，如果有则添加数字编号
   3. 筛选每篇文章的 AST，设置 header.id，检查文章之间的引用，将对源文件的链接替换成对目标 url 的链接
4. 每一篇文章渲染生成 html，先用 pandoc 生成 html 片段，再用 Jinja 生成完整 html 文件
5. 生成 index.html，传入网站信息和所有文章的元数据

# 待解决的问题

- [x] 代码块换行重复（Windows），需要指定换行格式为 LF
- [x] 表格样式错误
- [x] 代码着色
- [ ] 分析文章是否包含数学公式，决定页面是否加入 MathJax 外部引用
- [ ] 分析正文，中英文之间添加空格，包括不同 inline 之间的空格
- [x] 对输出的 HTML 进行压缩
- [ ] 开发新的基于 Item 的生成脚本
- [ ] 增加静态页面
- [ ] 修改代码块，增加行号开关，增加“全部复制”按钮
- [ ] 开发目录显示列表，显示在侧边栏，可收起
- [ ] 开发一套评论机制，显示在侧边栏，可收起

