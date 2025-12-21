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

# TODO 将每个文件抽象成 item，模仿 nanoc 定义明确的 item 处理流程


- [pangu.py](https://github.com/vinta/pangu.py)

pip install pandocfilters pangu pygments jinja2

'''



import os
import glob
import shutil
from datetime import datetime,date
import subprocess
import json
import argparse
from urllib.parse import quote,urljoin

from multiprocessing.pool import ThreadPool
# from tqdm import tqdm

import pandocfilters as pf
import pangu
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer, TextLexer
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, FileSystemLoader
from htmlmin import minify
from rcssmin import cssmin
from jsmin import jsmin



from nbconvert import HTMLExporter
import nbformat








PANDOC_TEMP_META = 'templates/meta.json'
PANDOC_TEMP_TOC = 'templates/toc.html'
PATH_POSTS = 'posts'
PATH_ASSETS = 'assets'
PATH_JINJA_TEMPS = 'templates'



class Item:
    def __init__(self, src, dst, url):
        self.src = src
        self.dst = dst
        self.url = url
    def generate(self):
        print(f'copying {self.src} to {self.dst}')
        shutil.copy(self.src, self.dst)

class CssItem(Item):
    def __init__(self, src, dst, url):
        super().__init__(src, dst, url)
    def generate(self):
        print(f'processing css {self.src}')
        with open(self.src, 'r', encoding='utf-8') as f:
            style = cssmin(f.read())
        with open(self.dst, 'w', encoding='utf-8') as f:
            f.write(style)

class JsItem(Item):
    def __init__(self, src, dst, url):
        super().__init__(src, dst, url)
    def generate(self):
        print(f'processing js {self.src}')
        with open(self.src, 'r', encoding='utf-8') as f:
            script = jsmin(f.read())
        with open(self.dst, 'w', encoding='utf-8') as f:
            f.write(script)

def create_item(src, dst, url):
    match os.path.splitext(src)[-1]:
        case '.css':    return CssItem(src, dst, url)
        case '.js':     return JsItem(src, dst, url)
        case _:         return Item(src, dst, url)





# Pandoc AST 的格式可以参考：
# https://github.com/mvhenderson/pandoc-filter-node/blob/master/index.ts
# 处理 AST，修改 permalink 为可读版本，整理静态资源链接，代码块着色，中英文间隔
# 处理 graphviz 绘图
def _ast_filter(key, value, post, site):
    def handle_link_image(value):
        attr,inlines,[url,title] = value
        if url.startswith('http://') or url.startswith('https://'):
            return value # 外部链接，不需要修改
        res = os.path.join(os.path.dirname(post.src), url)
        url = '/' + site.add_resource(res)
        return attr,inlines,(url,title)
    match key:
        case 'Str':
            return pf.Str(pangu.spacing_text(value))
        case 'Header':
            level,[id_,classes,kv],inlines = value
            # id_,classes,kv = attr
            return pf.Header(level, [quote(id_), classes, kv], inlines)
        case 'Link': return pf.Link(*handle_link_image(value))
        case 'Image': return pf.Image(*handle_link_image(value))
        case 'CodeBlock':
            # 使用 pygments 对代码着色，不使用 pandoc 自带的着色逻辑
            [id_,classes,kv],code = value
            # id_,classes,kv = attr
            try:
                if 0 == len(classes):
                    lexer = guess_lexer(code)
                else:
                    lexer = get_lexer_by_name(classes[0])
            except:
                lexer = TextLexer()
            return pf.RawBlock('html', highlight(code, lexer, HtmlFormatter()))




class Post:
    def __init__(self, src, outdir):
        base = os.path.splitext(os.path.basename(src))[0]
        self.date = date.fromisoformat(base[:10])
        self.src = src
        self.url = quote(base[11:])
        self.dst = os.path.join(outdir, self.url, 'index.html')
        self.draft = False




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

    def __init__(self, src, outdir):
        base = os.path.splitext(os.path.basename(src))[0]
        self.date = date.fromisoformat(base[:10])
        self.src = src
        self.url = quote(base[11:])
        self.dst = os.path.join(outdir, self.url, 'index.html')

    def process(self, site):
        print(f'rendering {self.src}')
        ast = self._pandoc_parse(self.src)
        meta = json.loads(self._pandoc_write(ast, PANDOC_TEMP_META))

        self.title = meta['title']
        self.draft = meta.get('draft', False)
        self.tags = meta.get('tags', meta.get('keywords', []))

        ast = pf.walk(ast, _ast_filter, self, site)
        self.toc = self._pandoc_write(ast, PANDOC_TEMP_TOC)
        self.html = self._pandoc_write(ast)



class NotebookItem:
    '''
    使用 nbconvert 转换笔记
    '''
    def __init__(self, src, outdir):
        self.src = src
        base = os.path.splitext(os.path.basename(src))[0]
        self.date = date.fromisoformat(base[:10])
        self.url = quote(base[11:])
        self.dst = os.path.join(outdir, self.url, 'index.html')
        self.title = base[11:].replace('-', ' ')
    def process(self, _):
        print(f'converting {self.src}')
        with open(self.src, 'r', encoding='utf-8') as f:
            content = nbformat.read(f, as_version=4)
        exporter = HTMLExporter(template_name="classic")
        body, resources = exporter.from_notebook_node(content)
        self.html = body
        self.toc = None
        # 渲染之后的html保存在成员变量中，可以使用 jinja 渲染





class Site:
    def __init__(self, title, src, out):
        self.title = title
        self.src_dir = src
        self.out_dir = out
        self.posts = [] # markdown
        self.notes = [] # jupyter notebook
        self.assets = []

    def add_items(self):
        self.add_assets()
        self.add_markdowns()
        # self.add_notebooks()

    def add_assets(self):
        asset_base = os.path.join(self.src_dir, PATH_ASSETS)
        assets = glob.glob('**', root_dir=asset_base, recursive=True)
        for url in assets:
            src = os.path.realpath(os.path.join(asset_base, url))
            if os.path.isfile(src):
                dst = os.path.join(self.out_dir, url)
                self.assets.append(create_item(src, dst, url))

    def add_markdowns(self):
        md_pattern = os.path.join(self.src_dir, PATH_POSTS, '**', '*.md')
        for src in glob.glob(md_pattern, recursive=True):
            self.posts.append(MarkdownItem(os.path.realpath(src), self.out_dir))

    def add_notebooks(self):
        nb_pattern = os.path.join(self.src_dir, PATH_POSTS, '**', '*.ipynb')
        for src in glob.glob(nb_pattern, recursive=True):
            self.notes.append(NotebookItem(os.path.realpath(src), self.out_dir))

    # 文件引用了静态文件，未被记录，将文件记录下来
    # TODO 引用计数？
    def add_resource(self, res, url=None, dst=None):
        src = os.path.realpath(res)
        found = filter(lambda x: x.src==src, self.assets)
        if any(found):
            return found[0].url
        if url is None:
            url = urljoin('files', os.path.basename(src))
        if dst is None:
            dst = os.path.join(self.out_dir, url)
        self.assets.append(create_item(src, dst, url))
        return url

    # 创建各个item需要的目录
    def prepare_dirs(self):
        target_dirs = [os.path.dirname(x.dst) for x in self.assets+self.posts+self.notes]
        for d in set(target_dirs):
            os.makedirs(d, exist_ok=True)

    def process(self, njobs):
        call_process = lambda p: p.process(self)
        with ThreadPool(njobs) as pool:
            # list(tqdm(pool.imap(call_process, self.posts), total=len(self.posts)))
            list(pool.imap(call_process, self.posts+self.notes))

    def drop_drafts(self):
        self.posts = [p for p in self.posts if not p.draft]

    def generate(self):
        for item in self.assets:
            item.generate()

        # post 和 index 都可以生成 html，可以共享一部分逻辑
        env = Environment(loader=FileSystemLoader(PATH_JINJA_TEMPS))
        post_tmp = env.get_template('post.html.jinja')
        for post in self.posts + self.notes:
            print(f'generating {post.url}')
            html = post_tmp.render(title=post.title, site_title=self.title, post=post)
            with open(os.path.join(self.out_dir, post.url, 'index.html'), 'w', encoding='utf-8') as f:
                f.write(minify(html))

        # 还要生成一个 index 页面
        recents = list(sorted(self.posts+self.notes, key=lambda p: p.date, reverse=True))
        idx_tmp = env.get_template('index.html.jinja')
        html = idx_tmp.render(title=self.title, posts=recents, now=datetime.now())
        with open(os.path.join(self.out_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(minify(html))







if '__main__' == __name__:
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--draft', action='store_true', help='render draft posts')
    parser.add_argument('-c', '--clean', action='store_true', help='cleanup')
    parser.add_argument('-j', '--jobs', default=os.cpu_count(), help='number of threads')
    parser.add_argument('-o', '--output', default='output', help='output directory')
    parser.add_argument('input', nargs='?', default=os.getcwd(), help='path to blog source')
    args = parser.parse_args()

    if args.clean:
        shutil.rmtree(args.output, ignore_errors=True)

    site = Site('songziming.cn', args.input, args.output)
    site.add_items()
    site.process(args.jobs)
    if not args.draft:
        site.drop_drafts()
    site.prepare_dirs()
    site.generate()
