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
    exporter = HTMLExporter(template_name="classic")
    body, resources = exporter.from_notebook_node(content)