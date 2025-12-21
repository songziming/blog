#!/usr/bin/env python

import glob

import nbformat
from nbconvert import HTMLExporter

'''
https://nbconvert.readthedocs.io/en/latest/nbconvert_library.html
'''


if '__main__' == __name__:
    notebooks = glob.glob('posts/*.ipynb')
    with open(notebooks[0], 'r', encoding='utf-8') as f:
        content = nbformat.read(f, as_version=4)

    # 这样渲染的页面是默认样式，和 jupyter 里面看到的一样，资源文件是 base64 内嵌在页面里的
    # 我们希望能定制页面样式
    exporter = HTMLExporter(template_name="classic")
    body, resources = exporter.from_notebook_node(content)

    with open('output/testnb.html', 'w', encoding='utf-8') as f:
        f.write(body)