---
title: 个人知识仓库系统
---

## 需求

一直有这样的需求，但是始终没有找到合适的软件。

要求：

- 使用markdown写作，不需要过于夸张的排版功能
- 可以使用LaTeX公式
- 可以使用表格
- 插入图片，快速插入屏幕截图，对图片的简单编辑（类似于微信）
- **可以方便地绘图，注意是绘图而不是图片，类似于Visio、TikZ那样的diagram**
- **对静态资源的自动管理**，例如文档里插入的图片，可以直接重命名保存到资源目录，自动引用计数，删除之后将图片文件也删除。
- 可以指定样式
- 可以发布成静态网站，配合静态网站生成器，一键直接发布网站。也可以特定页面分享，直接得到页面链接
- 可以离线使用，但是也提供同步功能。或者能够方便地借助其他平台实现数据同步（Github）
- 如果是web技术，能够直接在浏览器里使用
- 支持移动端，如果无法编辑，在移动端浏览也可以的

加粗的两条是现有软件做得不好的。

前面的是对软件功能的需求，除此之外，能提供下面的功能则更好：

- PDF文件管理和浏览、标注（annotation），替代一部分文献管理工具
- 只是仓库内部笔记交叉引用，自动生成引用拓扑图
- 更好用的编辑器，自动纠错
- 更好的中文显示，等宽（源代码）模式下宽度严格等于2英文字符，行高固定。

OneNote这类笔记软件符合大部分功能，但显得过于复杂，而且textbox非常讨厌。这类工具使用专有格式保存笔记，无法与其他工具配合。

Typora基本上满足了大部分需求，但是没有内置的绘图功能，资源管理做得也不好，必须手动维护。而且typora不开源，如果想扩展功能没法参考。

## 具体需求点分析

### 静态资源管理

这个可以由软件自动管理，复制图片进来就重命名，并放到assets文件夹下。自动维护一个kv数据库，记录着每张图片由哪些文档引用，引用数量是多少。如果在文档里编辑这个图片，就修改数据库中的记录。

### 内嵌绘图功能

Visio是一个很复杂的软件，但是开源的Web绘图库也有不少。既有tikz这样的文本式绘图，基于坐标精确绘制，也有diagram.io这类的所见即所得编辑器

### 核心编辑器

所谓软件核心的应该是一个编辑器，目前编辑体验最好的是Notion。虽然Notion不开源，但在Notion启发之下，已经有了不少开源编辑器项目，在设计上与Notion非常类似。

Notion之所以好用，主要是以block为单位进行编辑。

如果有开源的项目，可以在其基础上扩展，加入图像hook、自定义的diagram类型block，编辑时自动跳转到内联diagram编辑器。

适合在低分辨率的显示器上浏览。

## Electron笔记软件设计

基于Electron，使用Web技术实现一款笔记软件。

electron分为server和client两个进程，界面上的逻辑都是在client实现的。如果我们希望使用Typescript，electron服务端可以直接运行ts代码，但是网页里只能是JS，因此需要首先编译。

[示例项目](https://github.com/electron/electron-quick-start-typescript)在网页里同样使用Typescript，但是在package.json中加入了编译操作，执行tsc命令，根据`tsconfig.json`中的配置，将`src`目录下的每个Typescript文件转换成JS。

我们不需要webpack这类的生成器，因为不需要将多个ts编译成一个JS。况且，tsc本身就支持commonjs，可以使用import语法。

有可能要分出一部分任务在server进程执行，两种环境下的TS代码要明确区分。`manager`、`browser`、`common`三个目录，VSCode源代码就明确分成了这三个部分。

## 文本编辑器

核心组件是一个文本编辑器，目前网上有很多开源的editor，但是必须要了解这些组件的原理，才能完美地定制。

大部分editor都用到了`contenteditable`这个HTML属性，加上这个属性，HTML元素的内容就可以让用户编辑了。Notion、我来、Typora、CKEditor等软件都是使用的这个属性。但是这个属性问题很大，特别是WYSIWYG编辑器，用户选中文本之后，点击工具栏上的各种按钮来设置格式，体现到代码上，就是调用`doc.execCommand()`函数，向可编辑控件发送指令。

`contenteditable`属性的历史很长，这就导致有很多历史遗留问题，对于现代编辑器开发非常不方便。

vscode内置的monaco编辑器，实现方式则完全不同。在整个页面中搜索不到`contenteditable`属性，必然有一套不一样的实现手段。

> [Code-Editor-Design-Doc](https://github.com/microsoft/vscode/wiki/[WIP]-Code-Editor-Design-Doc)

Monaco完全是从零开始实现的，没有基于任何先有的框架，而且功能很多，针对代码编辑提供了minimap和diff-browser，并且支持搜索，支持弹出语法提示。

> Model-View v.s. MVVM
>
> Qt使用Model-View模式，monaco使用MVVM设计，区别在于后者多了一个ViewModel，作为视图和模型之间的连接（Controller）。如果是一些简单的控件，例如RadioButton、CheckBox，它们的模型非常简单，只有一个布尔变量，这时完全可以省去VM。但是对于monaco这样复杂的控件，使用ViewModel就非常有必要了，因为model和view之间的对应关系不是那么直接的。

传统native-gui-app的运行逻辑，是消息循环，更新界面的方法就是重新绘制界面。对于web-app，更新界面的方法就是修改DOM元素。我们可以认为DOM-tree就是一种新的framebuffer，浏览器就类似于video-adaptor，会帮我们将framebuffer里的数据自动转换成显示器上的图像。因此，对于web-app来说，所谓的渲染，就是生成DOM-tree，或者对于一个组件，就是生成一个子树。

接收用户事件的方法也类似，web-app甚至不需要自己监听全局的消息，浏览器会帮我们完成消息在dom-tree中的冒泡，各个控件只要自己处理自己的消息即可。原生应用需要自己轮询监听消息，而且需要自己实现组件层级的消息派发。

区别较大的地方是时序，以及动画。native-app有实时性要求，而且实现起来比较容易，但是在web-app中，若要实现动画效果，只能依靠css。

### Monaco实现机制

Monaco没有使用`contenteditable`属性，显示出来的行就是一个普通的div。

怎样实现光标？Monaco里的光标也是用div模拟出来的，并且注册了一个timer，不断改变光标的`visibility`属性，从而实现闪烁效果。实际上，Monaco能够多光标同时编辑，也是因为使用div模拟光标才能做到。

怎样实现输入？在光标的位置，正好有一个`textarea`元素，大小`1px*1px`，就放在光标元素的后面。并且注册这个元素的input事件。拦截`textarea`输入，然后将拦截到的输入文本转发给editor。怎样保证焦点？执行代码`viewHelper.focusTextArea()`，在鼠标事件的响应函数中处理就可以。

怎样实现选择？高亮显示部分是在`div.view-overlays`中显示的，与decoration放在一起。每一行代码除了可打印字符，还要显示许多其他信息，例如缩进的vertical-ruler，语法提示的下划线等。实现选择还要监听鼠标事件，这部分代码位于`src/vs/editor/browser/controller/mouseHandler.ts`，向顶层editorDom注册鼠标事件

在editor正文后面，有若干个`div.presentation`元素，这些元素提供光标、highlight，和其他的overlay功能。

### VueJS?

使用VueJS相比直接使用browser API确实方便一些，不过编辑器的需求过于特殊，对于这种复杂的控件，反而直接操作原始DOM更简单。

### 参考项目：eme

全名[Elegant Markdown Editor](https://github.com/egoist/eme)，是一个Vue+TypeScript+Electron开发的markdown编辑器，可以说和我们的需求非常类似了。



server

client

