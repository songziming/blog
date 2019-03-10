---
title: "MkDocs创建静态网站"
---

##### 使用Scss生成样式表

MkDocs并没有提供Sass支持，因此我们首先需要构建主题，再使用这个主题构建整个网站。

因此在Makefile中增加一个`theme`目标，使用命令`sass`，将`source`目录下的`*.scss`文件编译为单一的`main.css`，放在主题目录下。

##### 中英文之间自动插入空白

Word等排版软件往往内置这样的功能，但是浏览器不支持。Github上的项目[text-autospace.js](https://github.com/mastermay/text-autospace.js)能够实现类似的效果，而且完全自动化。

在HTML中引用脚本之后（需要jQuery），还需要在样式表中添加如下的规则：

~~~ css
body hanla:after {
    content:   ' ';
    display:   inline;
    font-size: 0.9em;
}

body code hanla,
body pre  hanla,
body kbd  hanla,
body samp hanla,
body ol > hanla,
body ul > hanla {
    display: none;
}
~~~