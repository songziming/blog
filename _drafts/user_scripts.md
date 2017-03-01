# User Script

用户脚本？

许多现代浏览器都有插件机制，开发者可以用 JavaScript 这类的语言轻松地编写浏览器插件，增加特殊的功能。UserScript 的作用与此类似，不过层次更高，开发更加容易。UserScript 就是一段 JavaScript 代码，每当一个页面加载完成之后，这段 JavaScript 就会自动执行，效果就和在调试工具的终端里执行 JavaScript 一样。UserScript 通常由浏览器的插件来管理，例如 FireFox 有 Greasemonkey，Webkit/Blink 内核的浏览器则有 Tampermonkey，而且这些工具支持的 UserScripts 接口相同，同样的 UserScript 在不同的管理插件下执行效果相同。

### 一个简单的 UserScript 示例

下面创建一个最简单的 UserScript，以 Chrome 浏览器的 Tampermonkey 为例。不同的 UserScripts 管理工具的操作方式有所区别，但应该大同小异。

首先打开 Tampermonkey 的 Dashboard，新增一个脚本。Tampermonkey 已经为我们准备好了一个基本的模板：

``` js
// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://tampermonkey.net/faq.php?ext=dhdg
// @grant        none
// ==/UserScript==
/* jshint -W097 */
'use strict';

// Your code here...
```

开头注释中是描述这个脚本的元信息，一个 UserScript 不能没有这一部分。各个字段的含义我们暂时不去关心，但是有一个 `@include` 字段很重要，模板中没列出来。`@include` 字段说明的是这个脚本作用于哪些网页，例如 `@include https://www.baidu.com/` 就表示仅仅针对百度网站首页有效，`@include https://www.baidu.com/*` 则表示 `www.baidu.com` 域名下的所有页面都会执行这个脚本。

添加一行 `@include` 属性，代码如下：

```
// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://tampermonkey.net/faq.php?ext=dhdg
// @grant        none
// @include      https://www.baidu.com/*
// ==/UserScript==
/* jshint -W097 */
'use strict';

alert("hello, world!");
```

将这个代码保存之后，新开一个页面，输入百度的网址 `https://www.baidu.com/` 然后回车，就会看到网页谈除了一个对话框：

![百度首页弹出对话框](/images/baidu-alert.png)

这个结果说明，我们的代码在百度的页面上执行了。

### 更改页面内容

下面做一个有点意思的。百度的首页标题是“百度一下，你就知道”，搜索框的右边也有一个“百度一下”的按钮，我们这里用一个脚本把它们改成“百度两下”，代码如下：

``` js
// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        https://tampermonkey.net/faq.php?ext=dhdg
// @grant        none
// @include      https://www.baidu.com/*
// ==/UserScript==
/* jshint -W097 */
'use strict';

document.title = '百度两下，你就知道';
$('#su').attr('value', '百度两下');
```

重新保存，刷新百度页面，就会得到如下结果：

![百度两下](baidu-twice.png)

这个例子中，用到了 DOM 中的 `document` 变量，还用到了 Jquery，这是因为百度的页面自身就引用了 JQuery，因此我们可以直接使用。
