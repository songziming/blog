---
title: 基本介绍
date: 2023-10-17
keywords: [pandoc, python, blog]
tags:
    - site-building
    - python
---


# 使用 Pandoc 的好处

目前来看，Pandoc 是功能最强的文本格式转换器。仅仅 markdown 一种格式，Pandoc 也提供了不少扩展样式。

例如：表格、定义列表、元数据块、角标、引用

## 这是第二级标题，有中文

中文标题不适合作为超链接锚点，转换拼音又可能出错。可以尝试一些 AI 辅助的转拼音模块，更准确一些

## 标题可以*倾斜*可以内嵌 `inline_code_span`

标题也有 inlines，当然加粗不一定有效（因为显示出来已经加粗）。

自动调用pangu在中英文之间添加空格，但必须位于同一个element才有效。如果某个段落中存在多个不同的inline，能否在**inline**之间增加空格？

pangu.py 只能处理 inline 内部文本。想在 tag 之间添加空格，必须仔细研究 pangu.js 的实现原理，然后自己开发。
