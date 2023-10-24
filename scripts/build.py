#! env python

import os
import re
from glob import glob

import json
import subprocess

from itertools import groupby
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

import pypinyin
import pandocfilters as pf
# import validators




PROJ_DIR    = os.path.abspath(os.getcwd())
TEMP_DIR    = os.path.join(PROJ_DIR, 'templates')
PANDOC_META = os.path.join(TEMP_DIR, 'meta.json')
PANDOC_TOC  = os.path.join(TEMP_DIR, 'toc.html')
SOURCE_DIR  = os.path.join(PROJ_DIR, 'posts')
TARGET_DIR  = os.path.join(PROJ_DIR, 'output')


JINJA_ENV   = Environment(loader=FileSystemLoader(TEMP_DIR))
JINJA_POST  = JINJA_ENV.get_template('post.html')
JINJA_INDEX = JINJA_ENV.get_template('index.html')


def _slugify(s):
    '''中文转换成拼音，英文全小写，特殊符号转换成下划线'''
    s = '_'.join(pypinyin.lazy_pinyin(s))
    return re.sub(r'[^a-z0-9]+', '_', s.lower())


def _is_external_url(url):
    '''判断是否为外部链接'''
    # return validators.url(url)
    return re.match(r'^https?://', url)



'''
调用 pandoc 解析 markdown，输出 JSON 格式的 AST，AST 的格式可以参考：
https://github.com/mvhenderson/pandoc-filter-node/blob/master/index.ts
'''

# 运行 pandoc，解析 markdown
def _pandoc_parse(md):
    cmd = ['pandoc', '-f', 'markdown', '-t', 'json', md]
    res = subprocess.run(cmd, capture_output=True)
    return json.loads(res.stdout.decode('utf-8'))

# 运行 pandoc，将 ast 渲染为 html
def _pandoc_write(ast, temp=None):
    ast = json.dumps(ast).encode()
    cmd = ['pandoc', '-f', 'json', '-t', 'html5', '--toc']
    if temp is not None:
        cmd += ['--template', temp]
    res = subprocess.run(cmd, input=ast, capture_output=True)
    return res.stdout.decode('utf-8')





















# pandoc filter
def ast_filter(key, value, format, meta):
    if key=='Header':
        # 标题很有可能是中文的，将其转换为英文，遇到重复则添加编号
        level,attr,inlines = value
        id,classes,kv = attr
        # ast_filter.counter += 1
        # return pf.Header(level, [f'header_{ast_filter.counter}', classes, kv], inlines)
        return pf.Header(level, [_slugify(id), classes, kv], inlines)

    elif key=='Link':
        attr,inlines,target = value
        url,title = target
        if _is_external_url(url):
            return # 外部链接，不需要修改

        # 相对于工程的路径、相对于文件的路径，都尝试一遍
        proj_root = os.path.join(PROJ_DIR, url)
        file_root = os.path.join(ast_filter.filedir, url)
        linkmap = ast_filter.file2link
        dst = linkmap.get(proj_root, linkmap.get(file_root))
        if dst is not None:
            return pf.Link(attr, inlines, [dst, title])
        else:
            print('cannot resolve target', url)


# 编辑 AST，修改标题链接和文件引用路径
def ast_transform(ast, file, file2link):
    ast_filter.headerid = 0
    ast_filter.filedir = os.path.dirname(file)
    ast_filter.file2link = file2link
    return pf.walk(ast, ast_filter, '', ast['meta'])












# # 渲染文章页面，pandoc 级别的渲染，获取html片段，而不是完整的html
# def generate_page(ast):
#     content = _pandoc_write(ast)
#     return JINJA_POST.render(body=content)


# # 输入所有文章的列表，生成主页的html
# def generate_index(posts):
#     return JINJA_INDEX.render(posts=posts)




# 读取一个 markdown 文件
# 从文件路径读取分类，从文件名读取时间和链接地址，再解析元数据和内容
# 返回一个字典，其中包括元数据和渲染后的 html 正文
def process_markdown(file):
    assert os.path.isabs(file)  # 必须是绝对路径

    filebase = os.path.splitext(os.path.basename(file))[0]
    try:
        date = datetime.strptime(filebase[:11], '%Y-%m-%d-')
        link = filebase[11:]
    except ValueError:
        date = None
        link = filebase

    ast = _pandoc_parse(file)
    # ast = modify_anchor(ast)
    meta = _pandoc_write(ast, PANDOC_META)
    meta = json.loads(meta)

    if 'date' in meta:
        date = datetime.strptime(meta['date'], '%Y-%m-%d')
    if 'link' in meta:
        link = meta['link']
    if date is None:
        print(f'no date in {file}')
        return None

    reladirs = os.path.relpath(file, SOURCE_DIR).split(os.sep)[:-1]
    categories = meta.get('categories', reladirs)
    permalinks = list(map(_slugify, categories + [link]))

    # TODO 改为自定义类
    # TODO 此时先不渲染 html，尝试复用缓存
    return {
        'source'    : file,
        'title'     : meta['title'],
        'date'      : date,
        'categories': categories,               # 多级分类目录，可以为空
        'keywords'  : meta.get('keywords', []), # 关键词列表，可以为空
        'permalinks': permalinks,               # 列表
        'ast'       : ast,
        # 'html'      : _pandoc_write(ast),
        # 'toc'       : _pandoc_write(ast, PANDOC_TOC),
    }






class StaticSiteBuilder:
    '''静态网站生成器，状态机'''

    def __init__(self, assets_dir='assets', source_dir='posts', template_dir='templates', output_dir='output'):
        assets_dir = os.path.abspath(assets_dir)
        source_dir = os.path.abspath(source_dir)
        template_dir = os.path.abspath(template_dir)
        output_dir = os.path.abspath(output_dir)
        self.assets_dir = assets_dir
        self.source_dir = source_dir
        self.output_dir = output_dir

        JINJA_ENV   = Environment(loader=FileSystemLoader(template_dir))
        self.PANDOC_META = os.path.join(template_dir, 'meta.json')
        self.PANDOC_TOC  = os.path.join(template_dir, 'toc.html')
        self.JINJA_POST  = JINJA_ENV.get_template('post.html')
        self.JINJA_INDEX = JINJA_ENV.get_template('index.html')

        assets = glob(os.path.join(assets_dir, '**', '*'), recursive=True)
        posts = glob(os.path.join(source_dir, '**', '*.md'), recursive=True)
        self.assets = {a:None for a in assets} # 源文件路径->输出文件路径
        self.posts = {p:None for p in posts} # 输入文件名->数据字典

    def add_assets(self, folder):
        '''找出所有的静态资源文件，这些资源也要复制到输出目录中'''
        self.assets = glob(os.path.join(folder, '*'), recursive=True)

    def add_posts(self, folder):
        '''添加源文件，记录在输入文件列表中'''
        for post in glob(os.path.join(folder, '*.md')):
            post = os.path.abspath(post)
            if post in self.posts:
                continue
            self.posts[post] = None

    def load_inputs(self):
        '''解析每一个输入文件，解析元数据和 AST'''
        self.posts = {k:process_markdown(k) for k,_ in self.posts.items()}

    def check_permalinks(self):
        '''检查有没有 permalink 冲突，如果有则根据时间排序编号'''
        file2link = [(k, v['permalinks']) for k,v in self.posts.items()]
        for dst,g in groupby(file2link, lambda x: x[1]):
            files = list(g)
            if 1 == len(files):
                continue
            print('\n  - '.join([f'conflict target {dst}', *files]))
            for i,f in enumerate(sorted(files, lambda f: self.posts[f]['date'])):
                self.posts[f]['permalinks'][-1] += f'_{i}'
        for k in self.posts.keys():
            permalinks = self.posts[k]['permalinks']
            self.posts[k]['link'] = '/'.join(['', *permalinks, ''])

    def check_links(self):
        '''检查文章内部的链接'''
        file2link = {k:v['permalinks'] for k,v in self.posts.items()}
        {**self.assets, **file2link}






def main():
    # 读取文章，提取元数据并渲染 html
    # TODO 使用线程池并行
    # TODO 比较时间戳，判断是否需要更新，需要更新才渲染 html
    posts = glob(os.path.join(SOURCE_DIR, '*.md'))
    posts = [process_markdown(p) for p in posts]

    # 如果遇到地址冲突的文章，则按照时间顺序编号
    posts2 = []
    for _,g in groupby(posts, lambda p: p['permalinks']):
        g = list(g)
        if len(g) == 1:
            posts2.append(g[0])
            continue
        g = sorted(g, key=lambda p: p['date'])
        print('\n -> '.join(['same target URL amongst:', *g]))
        for i,p in enumerate(g):
            p['permalinks'][-1] += f'_{i}'
            posts2.append(p)
    posts = posts2

    '''
    permalinks 为字符串列表，因为本地和 url 的地址拼接方式不同
    分别使用 os.path.join 和 '/'.join
    '''

    # 遍历每个文章，计算输出文件的路径和 URL 路径
    for p in posts:
        p['output'] = os.path.join(TARGET_DIR, *p['permalinks'], 'index.html')
        p['link'] = '/' + '/'.join(p['permalinks']) + '/'
        # os.makedirs(os.path.dirname(file), exist_ok=True)
        # with open(file, 'w') as f:
        #     f.write(JINJA_POST.render(**p))

    # 再次遍历所有文章，将文章之间的链接修改为正确的地址
    # 如果发现链接地址写错则打印错误信息，提醒作者修改
    # TODO 构建一个 map，源文件映射到 URL 链接
    # TODO markdown 文件内可以直接引用另一个 markdown 文件，甚至用通配符
    # TODO 修改标题锚点的过滤器也可以在此处执行
    linkmap = {p['source']:p['link'] for p in posts}
    for p in posts:
        p['ast'] = ast_transform(p['ast'], p['source'], linkmap)

    # permalinks = set([os.path.join(TARGET_DIR, *p['permalinks']) for p in posts])
    # for d in permalinks:
    #     os.makedirs(d, exist_ok=True)

    for p in posts:
        output = os.path.join(*p['permalinks'], 'index.html')
        abslink = '/' + '/'.join(p['permalinks']) + '/'
        del p['ast']
        print(output)
        print(abslink)
        print(p)



if '__main__' == __name__:
    main()
