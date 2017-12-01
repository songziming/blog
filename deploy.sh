#! /bin/bash

git branch -D gh-pages
git subtree split --prefix _site -b gh-pages
git push -f origin gh-pages:gh-pages
