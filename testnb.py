#!/usr/bin/env python

'''
https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
'''

import os
import glob
from traitlets.config import Config
import frontmatter # pip install python-frontmatter

import nbformat
# from nbconvert import HTMLExporter
from nbconvert.exporters.html import HTMLExporter
from nbconvert.preprocessors import Preprocessor, ExtractOutputPreprocessor

from jinja2 import DictLoader


class YamlCell(Preprocessor):
    '''从第一个cell里面解析yaml元数据'''
    def preprocess(self, nb, resources):
        if len(nb.cells) < 1 or 'markdown' != nb.cells[0].cell_type:
            return nb, resources

        metadata, content = frontmatter.parse(nb.cells[0].source)
        nb.meta = metadata
        nb.cells[0].source = content
        print(metadata)
        print(type(nb), dir(nb))
        return nb, resources


# 使用 python -m jupyter --path 检查 jupyter 默认搜索路径
# nbconvert 使用的 jinja2 template 默认路径是：
# C:\Users\zmsong\AppData\Local\Programs\Python\Python313\share\jupyter\nbconvert\templates
# 里面提供了多种模板，包括 lab、classic，使用里面的 index.html 渲染

dl = DictLoader({
    "footer": """
{%- extends 'lab/index.html.j2' -%}

{% block footer %}
FOOOOOOOOTEEEEER
{% endblock footer %}
"""
    })



class MyNbExporter(HTMLExporter):
    '''定制html渲染器，替换默认的jinja模板'''
    export_from_notebook = "My format"
    # def __init__(self, config):
    #     super().__init__()
    @property
    def template_paths(self):
        return super().template_paths + [os.path.realpath('templates/nb')]


if '__main__' == __name__:
    notebooks = glob.glob('posts/*.ipynb')
    with open(notebooks[0], 'r', encoding='utf-8') as f:
        content = nbformat.read(f, as_version=4)

    cfg = Config()
    cfg.MyNbExporter.preprocessors = [ YamlCell, ExtractOutputPreprocessor ]
        # 'nbconvert.preprocessors.ExtractOutputPreprocessor'

    # 这样渲染的页面是默认样式，和 jupyter 里面看到的一样，资源文件是 base64 内嵌在页面里的
    # 可以使用 ExtractOutputPreprocessor 将静态资源提取出来，放在 resources 里面
    # exporter = HTMLExporter(template_name='classic', config=cfg)
    exporter = MyNbExporter(config=cfg)
    body, resources = exporter.from_notebook_node(content)

    # 资源文件应该和 html 放在一个目录下
    for k,v in resources['outputs'].items():
        with open(os.path.join('output', k), 'wb') as f:
            f.write(v)

    with open('output/testnb.html', 'w', encoding='utf-8') as f:
        f.write(body)
