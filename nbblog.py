#!/usr/bin/env python

'''
这是 nbconverter Preprocessor
用来处理 notebook
'''

from nbconvert.preprocessors import Preprocessor


class YamlCell(Preprocessor):
    '''去掉第一个cell，使用yaml解析'''

    def preprocess(self, nb, resources):
        nb.cells = nb.cells[1:]
        return nb, resources