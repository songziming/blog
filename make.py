#! env python

import os
import re
import glob
import json
import shutil
import subprocess

import pypinyin
import pandocfilters as pf

from datetime import datetime
from itertools import groupby

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import HtmlFormatter

from jinja2 import Environment, FileSystemLoader
from htmlmin import minify



PANDOC_META = 'templates/meta.json'
PANDOC_TOC  = 'templates/toc.html'


def _pandoc_parse(md):
    cmd = ['pandoc', '-f', 'markdown', '-t', 'json', md]
    res = subprocess.run(cmd, capture_output=True)
    return json.loads(res.stdout.decode('utf-8'))

def _pandoc_write(ast, temp=None):
    cmd = ['pandoc', '-f', 'json', '-t', 'html5', '--toc', '--eol=lf']
    if temp is not None:
        cmd += ['--template', temp]
    res = subprocess.run(cmd, input=json.dumps(ast).encode(), capture_output=True)
    return res.stdout.decode('utf-8')

def _slugify(s):
    '''中文转换成拼音，英文全小写，特殊符号转换成下划线'''
    s = '_'.join(pypinyin.lazy_pinyin(s))
    return re.sub(r'[^a-z0-9]+', '_', s.lower())

def _css_minify(css):
    res = subprocess.run(['csso', css], capture_output=True)
    return res.stdout.decode('utf-8')





class Post:
    def __init__(self, file, rela):
        self.file = os.path.realpath(file)
        self.ast = _pandoc_parse(file)

        filepath = os.path.relpath(file, rela).split(os.sep)
        filebase = os.path.splitext(filepath[-1])[0]
        self.categories = filepath[:-1]
        self.slugified_categories = list(map(_slugify, self.categories))

        try:
            self.date = datetime.strptime(filebase[:11], '%Y-%m-%d-')
            self.slugified_title = _slugify(filebase[11:])
        except ValueError:
            self.date = None
            self.slugified_title = _slugify(filebase)

        meta = json.loads(_pandoc_write(self.ast, PANDOC_META))
        self.title = meta['title']
        self.draft = meta.get('draft', False)
        self.keywords = meta.get('keywords', [])
        if 'date' in meta:
            self.date = datetime.strptime(meta['date'], '%Y-%m-%d')
        if 'slug' in meta:
            self.slugified_title = meta['slug']

    def get_link(self):
        return '/'.join(['', *self.slugified_categories, self.slugified_title, ''])

    def get_output(self, html_dir):
        return os.path.join(html_dir, *self.slugified_categories, self.slugified_title, 'index.html')

    def render(self):
        self.toc = _pandoc_write(self.ast, PANDOC_TOC)
        self.html = _pandoc_write(self.ast)





def _is_external_url(s):
    return re.match(r'^https?://', s)

# Pandoc AST 的格式可以参考：
# https://github.com/mvhenderson/pandoc-filter-node/blob/master/index.ts
def _ast_filter(key, value, format, site):
    if key == 'Header':
        level,attr,inlines = value
        id,classes,kv = attr
        return pf.Header(level, [_slugify(id), classes, kv], inlines)

    elif key in ['Link', 'Image']:
        attr,inlines,target = value
        url,title = target
        if _is_external_url(url):
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





class Site:
    def __init__(self, title):
        self.title = title # 网站的标题
        self.posts = []
        self.pages = []     # 网站的页面（非博文非首页）
        self.assets = []    # (source, target)
        self.env = Environment(loader=FileSystemLoader('templates'))
        # TODO 各种目录都可以定制（assets、posts、templates）
        # TODO 读取 site.yaml 配置文件，提取上述信息


    def add_asset(self, source, target=None):
        if target is None:
            target = source
        source = os.path.realpath(source)
        if (not os.path.exists(source)) or os.path.isdir(source):
            return
        self.assets.append((os.path.realpath(source), target))

    def copy_assets(self, output_dir):
        for src,dst in self.assets:
            dst = os.path.join(output_dir, dst)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            if '.css'==os.path.splitext(src)[1]:
                open(dst, 'w').write(_css_minify(src))
            else:
                shutil.copy(src, dst)

    def add_posts_in(self, posts_dir='posts'):
        '''找出所有文章，解析其内容，可并行'''
        mds = glob.glob(os.path.join(posts_dir, '**', '*.md'), recursive=True)
        posts = [Post(md, posts_dir) for md in mds]
        self.posts = [p for p in posts if not p.draft]

    def check_permalinks(self):
        '''分析每个文章的链接，检查有无冲突，如有冲突则根据时间编号'''
        # TODO 不仅检查博文的目标地址，还应检查页面、静态文件、主页有无地址冲突
        get_link = lambda p: p.get_link()
        get_date = lambda p: p.date
        get_file = lambda p: p.file
        for l,g in groupby(sorted(self.posts, key=get_link), key=get_link):
            posts = list(sorted(g, key=get_date))
            if 1 == len(posts):
                continue
            print('\n  - '.join([
                f'target {l} shared by multiple files:',
                *map(get_file, posts)
            ]))
            for i,p in enumerate(posts):
                p.slugified_title += f'_{i}'

    def filter_documents(self):
        '''编辑每篇文章的内容，修改标题锚点，检查文章之间的链接，可并行'''
        _ast_filter.filemap = {p.file:p.get_link() for p in self.posts}
        for post in self.posts:
            _ast_filter.filedir = os.path.dirname(post.file)
            post.ast = pf.walk(post.ast, _ast_filter, '', self)

    def build_posts(self, output_dir):
        '''所有文章渲染为 html，写入输出文件'''
        tmp = self.env.get_template('post.html.jinja')
        for post in self.posts:
            ofile = post.get_output(output_dir)
            os.makedirs(os.path.dirname(ofile), exist_ok=True)
            post.render()
            html = tmp.render(title=post.title, site_title=self.title, post=post)
            with open(ofile, 'w', encoding='utf-8') as f:
                f.write(minify(html))

    def build_pages(self, output_dir):
        # 还有一些静态页面需要生成
        # TODO 静态页面也可以使用 md 或者 html，由用户决定内容
        # TODO 如果是 markdown 则使用 pandoc 解析再使用 jinja 渲染
        # TODO 如果是 html 则直接使用 jinja 渲染
        pass

    def build_index(self, index):
        recents = list(sorted(self.posts, key=lambda p: p.date, reverse=True))
        idx = self.env.get_template('index.html.jinja')
        html = idx.render(title=self.title, posts=recents, now=datetime.now())
        with open(index, 'w', encoding='utf-8') as f:
            f.write(minify(html))

    def build(self, output_dir='output', rebuild=False):
        if rebuild:
            shutil.rmtree(output_dir, ignore_errors=True)
        os.makedirs(output_dir, exist_ok=True)
        self.copy_assets(output_dir)
        self.build_posts(output_dir)
        self.build_pages(output_dir)
        self.build_index(os.path.join(output_dir, 'index.html'))


if '__main__' == __name__:
    # TODO 命令行参数控制是否渲染 draft
    site = Site('songziming.cn')

    # 指定所有输入
    site.add_asset('CNAME')
    site.add_asset('.nojekyll')
    site.add_asset('favicon.ico')
    for f in glob.glob('assets/**', recursive=True):
        site.add_asset(f)
    site.add_posts_in('posts')

    # 中间处理
    site.check_permalinks()
    site.filter_documents()

    # 生成
    site.build('output', True)

