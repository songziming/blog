---
title: 用 GitCafe 托管静态博客
category: 建站
tags:
- hexo
- gitcafe
---

以前，我都是把网站托管在自己的 DigitalOcean VPS 上。由于最初搞的是 Ghost 博客引擎，因此需要一个能够运行 Node.js 的服务器。恰好 Github 送出的教育优惠中包含了 DigitalOcean 的优惠，于是就用上 VPS。

在那之前，我还尝试过 Github Pages 托管静态网站，还尝试过一个很小众的 Stdyun，但是后来莫名其妙地就消失了（据说是被美团云收购的）。现在，博客系统已经是 Hexo，静态网站的托管也完全能够满足需求，DigitalOcean 上面的余额也快用完了，我有开始寻找新的静态网站托管服务。

由于博客的大部分访问都来自国内，因此 Github Pages 并没有被我采用。搜索过程中，无意中发现了 GitCafe 也提供一个 Pages 服务。GitCafe 是上海的一家公司，定位就是国内的 Github，因此他们的 GitCafe Pages 服务应该也不会慢。

GitCafe 网站上有[关于创建 Pages 的帮助](https://gitcafe.com/GitCafe/Help/wiki/Pages-%E7%9B%B8%E5%85%B3%E5%B8%AE%E5%8A%A9)。

我全部的项目都托管在 Github 上面，GitCafe 只使用他们的网站托管功能。首先在 GitCafe 上注册了用户，添加 SSH 公钥，创建一个和用户名相同名字的项目。

GitCafe Pages 的行为和 Github Pages 类似，也是将网站放在特定的分支下（这里叫做 `gitcafe-pages`）。首先在本地创建一个项目目录，创建一个文件，添加项目上游地址，切换到 `gitcafe-pages` 分支并提交。

``` bash
mkdir gitcafe && cd gitcafe
git init
echo 'hello' > index.html
git add --all
git commit -m 'created first file'
git remote add origin git@gitcafe.com:<用户名>/<用户名>.git
```

这样，在浏览器中输入 `<用户名>.gitcafe.io` 就可以看到 `index.html` 中的内容。

如果希望使用自己的域名，可以在“项目设置”--“Pages服务”下添加自己的域名，然后在自己的域名注册商那里添加一个指向 `gitcafe.io` 的 CNAME 记录。

### Hexo 设置

最后，方便 Hexo 博客的部署工作，向 Hexo 的 `_config.yml` 文件添加以下内容：

``` yaml
deploy:
    type: git
    repo: git@gitcafe.com:<用户名>/<用户名>.git
    branch: gitcafe-pages
```

这段配置表示执行 `hexo deploy` 命令的时候自动上传到刚刚创建的 Git 项目的 gitcafe-pages 分支下。

部署到 Git 项目需要用到 `hexo-deployer-git` 插件，使用下面的命令安装：

``` bash
sudo npm install --save hexo-deployer-git
```

最后执行 `hexo deploy`，成功之后便可以感受飞一般的访问速度了。
