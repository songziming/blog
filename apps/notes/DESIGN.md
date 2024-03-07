# 编辑器控件设计

基于 slatejs 定制的富文本编辑器，满足个人笔记的要求。

# Schema

Leaf 元素是 {text: ""}。Leaf 可以有加粗、倾斜等样式，作为与 text 平级的成员。

Element 是拥有 children 成员的节点。Element 子元素是 Leaf 或者其他 Element。

有些 Element 属于 Inline，有些属于 Block。

一般的 Block 包含 Inline 和 Leaf，例如正文、标题。
有些 Block 包含其他 Block，例如代码块、列表块，引用文字块。
还有的 Block 不含文字，如 Image、Bookmark、FileRef。
还有的 Block 比较特殊，如 Table、DataFrame。

各种 Element 通过 type 字段区分：

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
