# 编辑器控件设计

基于 slatejs 定制的富文本编辑器，满足个人笔记的要求。

Slate 也是 model-view 设计，view 就是 React 组件，核心 model 是文档数据模型。

编辑操作就是对文档模型的更新，通过 Transforms 实现。

# Schema

整个文档是一棵树。节点有 Leaf、Element 两类。拥有 text 成员就是 Leaf，拥有 children 成员就是 Element。

Leaf 除了 text，还可以有其他字段，表示加粗、倾斜等样式。

Element.children 可以包含 Leaf 或者其他 Element。

有些 Element 属于 Inline，有些属于 Block，但这需要我们判断。我们可以给 Element 加上 type 字段：

- Inline 类型：
  - type="codespan"
  - type="mathspan"
  - type="linkspan" href=""
- 包含文本的 Block：
  - type="para"
  - type="header" level=1|2|3
  - type="math"
  - type="codeline"
  - type="listitem" level=0|1|2|...
  - type="todoitem" level=0|1|2|... checked=true|false
  - type="toggleitem" level=
  - type="toggleheader" level=
- 包含其他 Block 的 Block：
  - type="quote"
  - type="callout"
  - type="codeblock"
  - type="listblock" subtype=numbered|bulleted|toggle|todo
- 不含可编辑文本的 Block：
  - type="image" source="file://..."
  - type="bookmark" source="..."
  - type="embed" subtype=video|audio|file
  - type="divider"
- 剩下的不好分类的 Block：
  - Table，区分单元格，



# TODO

- [ ] 支持插入图片，简单的图片编辑（尺寸、裁剪）

- [ ] 支持带格式的复制粘贴
- [ ] 支持图片、文件的复制粘贴，支持拖拽
