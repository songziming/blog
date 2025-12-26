#!/usr/bin/env python

'''
https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html

notebook file format doc:
https://nbformat.readthedocs.io/en/latest/format_description.html
'''

import os
import json
import glob
from traitlets.config import Config
import frontmatter # pip install python-frontmatter

import nbformat
from nbconvert.exporters.html import HTMLExporter
from nbconvert.preprocessors import Preprocessor, ExtractOutputPreprocessor



class YamlCell(Preprocessor):
    '''从第一个cell里面解析yaml元数据'''
    def preprocess(self, nb, resources):
        if len(nb.cells) < 1 or 'markdown' != nb.cells[0].cell_type:
            return nb,resources

        metadata, content = frontmatter.parse(nb.cells[0].source)
        nb.meta = metadata
        nb.cells[0].source = content
        return nb,resources


# nbconvert 应该提供了其他使用pandoc的方法
class PandocConverter(Preprocessor):
    '''使用pandoc转换markdown'''
    def preprocess(self, nb, resources):
        for cell in nb.cells:
            pass
            # meta,rc,toc,html =


class Scope(Preprocessor):
    def preprocess(self, nb, resources):
        with open('output/nb_ast.json', 'w') as f:
            json.dump(nb, f)
        return nb,resources


class MyNbExporter(HTMLExporter):
    '''定制html渲染器，替换默认的jinja模板，从我们的目录下搜索jinja2模板'''
    @property
    def template_paths(self):
        '''默认搜索路径可以用命令查看：python -m jupyter --path'''
        return [os.path.realpath('templates/nb')]
    def _template_file_default(self):
        return 'notebook'


if '__main__' == __name__:
    notebooks = glob.glob('posts/*.ipynb')
    with open(notebooks[0], 'r', encoding='utf-8') as f:
        content = nbformat.read(f, as_version=4)

    cfg = Config()
    cfg.MyNbExporter.preprocessors = [ YamlCell, ExtractOutputPreprocessor, Scope ]

    exporter = MyNbExporter(config=cfg)
    body, resources = exporter.from_notebook_node(content)

    # 资源文件应该和 html 放在一个目录下
    for k,v in resources['outputs'].items():
        with open(os.path.join('output', k), 'wb') as f:
            print('saving', k)
            f.write(v)

    with open('output/testnb.html', 'w', encoding='utf-8') as f:
        f.write(body)
