# Song Ziming's Blog

this is my blog, generated with jekyll.

Published on Github Pages, but is generated locally.

To push content to an existing branch, potentially over-writing current files, use the following command:

```bash
git subtree push --prefix _site origin gh-pages
```

but git might report conflict, to avoid this:

```bash
git push origin `git subtree split --prefix _site gh-pages`:gh-pages --force
```

http://www.damian.oquanta.info/posts/one-line-deployment-of-your-site-to-gh-pages.html

首先，需要保证 `_site` 目录不在 `.gitignore` 文件中。

下面的命令需要在 master 分支中执行

```bash
git branch -D gh-pages 	# 首先将本地的 gh-pages 分支删除
git subtree split --prefix _site -b gh-pages # 从本地的 _site 目录分离出一个新的 gh-pages 分支
git push -f origin gh-pages:gh-pages # 将 gh-pages 分支上传至服务器
```