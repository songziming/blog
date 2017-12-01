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