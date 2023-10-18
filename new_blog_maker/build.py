#! env python

'''
静态网站构建脚本
'''

import os
import glob
import json

import subprocess

import pandocfilters as pf
import pangu

'''
关于 pandoc AST，可以参考：
https://github.com/mvhenderson/pandoc-filter-node/blob/master/index.ts
'''



# 运行 pandoc 将 markdown 转换为 html，输出的 html 里面还有元数据
def run_pandoc(src):
    cmd = ['pandoc', '-f', 'markdown', '-t', 'html5', '--toc', '--template', 'template.html', src]
    res = subprocess.run(cmd, capture_output=True)
    return res.stdout.decode('utf-8')


def parse_markdown(md):
    cmd = ['pandoc', '-f', 'markdown', '-t', 'json', md]
    res = subprocess.run(cmd, capture_output=True)
    return json.loads(res.stdout.decode('utf-8'))


def render_html(ast):
    ast = json.dumps(ast).encode()
    cmd = ['pandoc', '-f', 'json', '-t', 'html5']
    res = subprocess.run(cmd, input=ast, capture_output=True)
    return res.stdout.decode('utf-8')


def get_meta(ast):
    if 'meta' in ast:
        return ast['meta'] # new API
    elif ast[0]:
        return ast[0]['unMeta'] # old API


def reset_anchor(key, value, _, __):
    if key=='Header':
        level, attrs, inlines = value
        _, classes, kv = attrs
        reset_anchor.counter += 1
        return pf.Header(level, [f'header_{reset_anchor.counter}', classes, kv], inlines)


def modify_ast(ast):
    reset_anchor.counter = 0
    return pf.walk(ast, reset_anchor, '', {})


'''
我们已经知道了 pandoc AST 的结构，完全可以自己生成 html
不过我们只需要关心 meta 的解析，其他的不重要
meta 数据也有多种类型，我们只需要支持 Str、Inlines 两类，因为这两类可以转换为纯文本
'''

def parse_file(md):
    ast = parse_markdown(md)
    ast2 = modify_ast(ast)
    # print(ast2['blocks'])
    # return
    # html = render_html(ast2)
    html = ''.join([gen_pandoc_elt(b) for b in ast2['blocks']])
    html = pangu.spacing_text(html)
    print(html)


# 渲染 markdown
def convert_file(md):
    text = run_pandoc(md)
    # print(text)

    [meta,toc,body] = text.split(os.linesep + os.linesep)
    # meta,_,html = text.partition('\n')
    meta = json.loads(meta)

    # 再把 html 片段集成到 jinja2 模板中
    print('meta')
    print(meta)

    print('toc')
    print(toc)

    print('body')
    print(body)

    # 根据元数据里设置的 canonical-url，生成输出的 <URL>/index.html



#-------------------------------------------------------------------------------
# 自己开发一套 html writer，不再依赖 pandoc

# 从显示效果来看，element 分为 block、inline 两种
# 但对应到 html，不需要区分，而是应该分为三类：
# 1. 由 inlines 组成的
# 2. 由次一级 blocks 组成的
# 3. 由纯文本组成的


# pandoc AST 类型很丰富，但 markdown 只会用到有限的节点
def gen_pandoc_elt(elt):
    ELT_WRITERS = {
        'Null'          : lambda _: '',
        'HorizontalRule': lambda _: '<hr/>',
        'Space'         : lambda _: '&nbsp;',
        'SoftBreak'     : lambda _: '&shy;',
        'LineBreak'     : lambda _: '&NewLine;',

        'Str'           : lambda x: x,
        'Emph'          : lambda x: gen_tag_sub('em', x),
        'Strong'        : lambda x: gen_tag_sub('strong', x),
        'Strikeout'     : lambda x: gen_tag_sub('s', x),
        'Superscript'   : lambda x: gen_tag_sub('sup', x),
        'Subscript'     : lambda x: gen_tag_sub('sub', x),
        'SmallCaps'     : lambda x: gen_tag_sub('span', x, classes=['scap']),
        'Quoted'        : gen_quote_tag,

        'Code'          : lambda x: gen_tag('code', x[1], x[0]), # [Attr, string]
        'Link'          : lambda x: gen_tag_sub('a', x[1], x[0], href=x[2]), # [Attr, Array<Inline>, Target]
        'Image'         : lambda x: gen_tag_sub('img', x[1], x[0], src=x[2]), # [Attr, Array<Inline>, Target]

        # 'Cite'          : [Array<Citation>, Array<Inline>];
        # 'Code'          : [Attr, string];
        # 'Math'          : [MathType, string];
        # 'RawInline'     : [Format, string];
        # 'Note'          : Array<Block>;
        # 'Span'          : [Attr, Array<Inline>];

        'Plain'         : lambda x: gen_tag_sub('p', x),
        'Para'          : lambda x: gen_tag_sub('p', x),
        'Header'        : lambda x: gen_tag_sub(f'h{x[0]}', x[2], x[1]), # [number, Attr, Array<Inline>]
        'CodeBlock'     : lambda x: gen_tag('code', x[1], x[0]), # [Attr, string]
        # 'LineBlock'     : 1,
        # 'CodeBlock'     : 1,
        # 'RawBlock'      : 1,
        # 'BlockQuote'    : 1,
        # 'OrderedList'   : 1,
        # 'BulletList'    : 1,
        # 'DefinitionList': 1,
    }

    # if 'c' not in elt:
    #     print('not a valid element')
    #     print(elt)
    #     return ''

    kind = elt['t']
    data = elt.get('c')
    if kind not in ELT_WRITERS:
        print(f'pandoc node type {kind} not supported')
        return ''
    return ELT_WRITERS[kind](data)


def gen_tag(tag, content, attr=None, classes=[], **kwargs):
    if attr is not None:
        id, cls, kvs = attr
        cls += classes
        if 0 != len(cls):
            kvs.append(('class', ' '.join(cls)))
        if id:
            kvs.append(('id', id))
        kvs += list(kwargs.items())
        extra = ''.join([f' {k}="{v}"' for k,v in kvs])
    else:
        extra = ''
    return f'<{tag}{extra}>{content}</{tag}>'


def gen_tag_sub(tag, subs, attr=None, classes=[]):
    content = ''.join([gen_pandoc_elt(e) for e in subs])
    return gen_tag(tag, content, attr, classes)




def gen_quote_tag(data):
    # 引用文本，需要区分单引号还是双引号
    quotetype, inlines = data
    quotetype = quotetype['t']
    content = ''.join([gen_pandoc_elt(e) for e in inlines])
    if 'SingleQuote' == quotetype:
        return '&#145;' + content + '&#146;'
    elif 'DoubleQuote' == quotetype:
        return '&#147;' + content + '&#148;'






def main():
    posts = glob.glob('posts/*.md')
    for post in posts:
        # convert_file(post)
        parse_file(post)



if '__main__' == __name__:
    main()
