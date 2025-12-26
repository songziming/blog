#!/usr/bin/env python

'''
负责处理 markdown，转换成 html
输入 markdown str，输出 metadata dict、resources dict、toc html、html str
'''

import json
import subprocess
import pandocfilters as pf

# 调用 pandoc，从 stdin 读取输出，从 stdout 获取输出

PANDOC_TEMP_META = 'templates/meta.json'
PANDOC_TEMP_TOC = 'templates/toc.html'

def _pandoc_parse(md):
    '''读取 markdown，转换为 json AST'''
    cmd = ['pandoc', '-f', 'markdown', '-t', 'json']
    res = subprocess.run(cmd, stdin=md.encode(), capture_output=True)
    return json.loads(res.stdout.decode('utf-8'))

def _pandoc_write(ast, tmp=None):
    '''将 json AST 渲染成 html'''
    cmd = ['pandoc', '-f', 'json', '-t', 'html5', '--toc', '--eol=lf']
    cmd += ['--template', tmp] if tmp else []
    res = subprocess.run(cmd, input=json.dumps(ast).encode(), capture_output=True)
    return res.stdout.decode('utf-8')



def _ast_filter(key, value, _, resources):
    pass


def process_markdown(md):
    ast = _pandoc_parse(md)
    meta = json.loads(_pandoc_write(ast, PANDOC_TEMP_META))

    resources = {}
    ast = pf.walk(ast, _ast_filter, None, resources)
    toc = _pandoc_write(ast, PANDOC_TEMP_TOC)
    html = _pandoc_write(ast)

    return meta, resources, toc, html
