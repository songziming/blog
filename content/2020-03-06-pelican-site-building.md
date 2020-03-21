---
title: 使用Pelican构建静态网站
date: 2020-03-06
---

## 安装

``` sh
sudo python3 -m pip install pelican Markdown
```

Pelican提供了一个工具，可以直接生成项目，但还是从零开始写配置文件比较方便。

许多功能都是不需要的，例如文章归档、作者介绍、分类、标签，以及RSS推送，这些都可以在配置文件里禁用：

``` py
# disable archive, categories, tags and authors
DIRECT_TEMPLATES = [ 'index' ]
CATEGORY_SAVE_AS = ''
AUTHOR_SAVE_AS   = ''
TAG_SAVE_AS      = ''

# disable feeds
FEED_ALL_ATOM         = None
CATEGORY_FEED_ATOM    = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM      = None
AUTHOR_FEED_RSS       = None
```

## 主题

自定义theme，需要提供一个目录，结构如下：

```
theme/
├── static/
└── templates/
```

其中，`static`存放css、js等静态资源，`templates`存放Jinja2模板。我们禁用了归档、分类、标签等页面，只剩下主页和文章页面两类，因此需要提供的模板只有`index.html`和`article.html`。

## 定制

安装一个插件`markdown-cjk-spacing`，可以自动在中英文之间插入空格。然而，这个插件只对文章正文有效，而且只有当中英文处于同一级tag中才会生效。

如果希望在标题中也加入中英文间隔，可以编写自己的Jinja2 filter，并且在主题模板中应用我们开发的filter。然而正文的中英文间隔，则只能改进markdown插件实现。

此外还有summary长度计算的问题，默认使用单词数，对CJK不友好，Github上已经有了[Issue](https://github.com/getpelican/pelican/issues/1180)。目前还没有更好的解决方案，可以在Jinja2模板中引入`truncate`，截取文章正文前方固定长度的子串。
