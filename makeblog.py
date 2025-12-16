#!/usr/bin/env python

'''
静态网站生成工具

为什么自己开发一套生成器，而不是使用现有的？
- SSG 其实不复杂
- 不喜欢 nodeJS 和 Ruby，希望使用 Python
- 希望使用最强大的 markdown 工具：Pandoc
- 需要定制自己的绘图工具，最好可以在 vscode 里面编辑，不仅重视生成效果，也重视编辑体验

# 在 Python 里面使用 Pandoc
pandoc 不是 python 模块，是 haskell 开发的独立工具
如何在 Python 里面使用 Pandoc？有两个模块：pandoc、pypandoc，但这两个模块都需要单独安装 pandoc
既然只是对 pandoc 命令的封装，不如我们自己使用 subprocess 直接运行 pandoc

使用我们的 pandoc filter？
Pandoc 支持 filter，可以对 AST 进行处理。filter 可以用 python，不一定要用 haskell
我们可以通过 filter 实现的功能：
- 处理章节链接（使用拼音）
- 调整引用的静态资源路径
- 使用pygment对代码块着色
- 中英文之间添加空格
手动方法是：
- 调用 pandoc 将 markdown 转换为 json，将 json 读取到 python 里面
- 执行 filter，修改 AST

# TODO 支持其他类型的页面（jupyter notebook）


- [pangu.py](https://github.com/vinta/pangu.py)

pip install pandocfilters pangu pygments jinja2

'''



import argparse

import pandocfilters as pf
import pangu
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, FileSystemLoader

import os
import glob
import shutil
# import datetime
# import datetime.now
from datetime import datetime,date
import subprocess
import json









def _slugify(s):
    '''使用拼音作为 permalink'''
    return s




class MarkdownItem:
    @staticmethod
    def _pandoc_parse(file):
        '''读取 markdown，转换为 json AST'''
        cmd = ['pandoc', '-f', 'markdown', '-t', 'json', file]
        res = subprocess.run(cmd, capture_output=True)
        return json.loads(res.stdout.decode('utf-8'))

    @staticmethod
    def _pandoc_write(ast, tmp=None):
        '''将 json AST 渲染成 html'''
        cmd = ['pandoc', '-f', 'json', '-t', 'html5', '--toc', '--eol=lf']
        cmd += ['--template', tmp] if tmp else []
        res = subprocess.run(cmd, input=json.dumps(ast).encode(), capture_output=True)
        return res.stdout.decode('utf-8')

    def __init__(self, file, base):
        self.file = os.path.realpath(file)
        self.rela = os.path.relpath(self.file, base)

    def process(self):
        self.ast = self._pandoc_parse(self.file)

        # 从路径解析分类
        path = self.rela.split(os.sep)
        self.categories = path[:-1]

        # 从文件名解析日期、链接
        base = os.path.splitext(path[-1])[0]
        try:
            self.date = date.fromisoformat(base[:10])
            self.link = _slugify(base[11:])
        except ValueError:
            self.date = None
            self.link = _slugify(base)

        # 从 yaml frontmatter 解析标题、关键词
        meta = json.loads(self._pandoc_write(self.ast, 'templates/meta.json'))
        self.title = meta['title']
        self.draft = meta.get('draft', False)
        self.tags = meta.get('tags', meta.get('keywords', []))

    def get_permalink(self, base_dir):
        return os.path.join(base_dir, self.link, 'index.html')

    def generate(self):
        self._pandoc_write(self.ast)


class Site:
    def __init__(self, base):
        self.base = base
        self.posts = []
        self.assets = {} # local_path -> url
        self.env = Environment(loader=FileSystemLoader('templates'))

    def add_asset(self, file, url):
        if file not in self.assets:
            self.assets[file] = url

    def add_post(self, post):
        self.posts.append(post)

    def build(self, output_dir, clean=False):
        if clean:
            shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)
        self._copy_assets(output_dir)
        self._build_posts(output_dir)
        self._build_index(os.path.join(output_dir, 'index.html'))

    def _copy_assets(self, output_dir):
        for src,dst in self.assets.items():
            dst = os.path.join(output_dir, dst)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            # if '.css'==os.path.splitext(src)[1]:
            #     with open(dst, 'w') as f:
            #         min_css = _css_minify(src)
            #         f.write(min_css)
            # else:
            #     shutil.copy(src, dst)
            shutil.copy(src, dst)

    def _build_posts(self, output_dir):
        '''所有文章渲染为 html，写入输出文件'''
        tmp = self.env.get_template('post.html.jinja')
        for post in self.posts:
            ofile = post.get_permalink(output_dir)
            os.makedirs(os.path.dirname(ofile), exist_ok=True)
            post.generate()
            html = tmp.render(title=post.title, site_title='site title', post=post)
            with open(ofile, 'w', encoding='utf-8') as f:
                # f.write(minify(html))
                f.write(html)

    def _build_index(self, index):
        recents = list(sorted(self.posts, key=lambda p: p.date, reverse=True))
        idx = self.env.get_template('index.html.jinja')
        html = idx.render(title='site title', posts=recents, now=datetime.now())
        with open(index, 'w', encoding='utf-8') as f:
            f.write(minify(html))


# Pandoc AST 的格式可以参考：
# https://github.com/mvhenderson/pandoc-filter-node/blob/master/index.ts
# 处理 AST，修改 permalink 为可读版本，整理静态资源链接，代码块着色，中英文间隔
# 处理 graphviz 绘图
def _ast_filter(key, value, format, site):
    if key == 'Str':
        return pf.Str(pangu.spacing_text(value))
    elif key == 'Header':
        level,attr,inlines = value
        id,classes,kv = attr
        return pf.Header(level, [_slugify(id), classes, kv], inlines)

    elif key in ['Link', 'Image']:
        attr,inlines,target = value
        url,title = target
        if url.startswith('http://') or url.startswith('https://'):
            return # 外部链接，不需要修改

        # 应该基于 posts 目录、文件所在目录分别计算两个相对路径
        if url not in _ast_filter.filemap:
            url = os.path.realpath(os.path.join(_ast_filter.filedir, url))
        if url in _ast_filter.filemap:
            url = _ast_filter.filemap[url]
        else:
            print('cannot resolve link target', url)
        return pf.Link(attr, inlines, [url, title])

    elif key == 'CodeBlock':
        # 使用 pygments 对代码着色，不使用 pandoc 自带的着色逻辑
        attr,code = value
        id,classes,kv = attr
        try:
            if 0 == len(classes):
                lexer = guess_lexer(code)
            else:
                lexer = get_lexer_by_name(classes[0])
        except:
            lexer = TextLexer()
        return pf.RawBlock('html', highlight(code, lexer, HtmlFormatter()))





if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--draft', action='store_true', help='render draft posts')
    parser.add_argument('-M', '--no-minify', action='store_true', help='do not minify')
    parser.add_argument('-o', '--output', default='output', help='output directory')
    parser.add_argument('input', nargs='?', default=os.getcwd(), help='path to blog source')
    args = parser.parse_args()
    print(f'input={args.input} output={args.output}, M={args.no_minify}, d={args.draft}')

    asset_base = os.path.join(args.input, 'assets')
    template_base = os.path.join(args.input, 'templates')

    site = Site(args.input)

    # 添加资源文件
    assets = glob.glob(os.path.join(asset_base, 'assets/**'), recursive=True)
    for a in filter(os.path.isfile, assets):
        real = os.path.realpath(a)
        rela = os.path.relpath(real, asset_base)
        site.add_asset(real, rela)

    # 添加文章
    mdfiles = glob.glob(os.path.join(args.input, 'posts/*.md'))
    for md in mdfiles:
        post = MarkdownItem(md, template_base)
        post.process()
        site.add_post(post)

    # TODO 检查不同文章的 url 是否冲突，如果冲突则添加数字后缀编号

    # TODO 对每个文章的 ast 执行 filter，处理正文

    site.build(args.output)