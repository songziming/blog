#! env python


'''
自己开发的 pandoc AST --> html 生成器

这不是必须的，也可以使用 pandoc 生成 html
然而元数据字段类型也是 AST Element，需要一套函数转换为标准字符串
'''




def ast_to_html(ast):
    return ''.join([gen_ast_node(b) for b in ast['blocks']])

def gen_ast_node(node):
    WRITERS = {
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

    kind = node['t']
    data = node.get('c')
    if kind not in WRITERS:
        print(f'pandoc node type {kind} not supported')
        return ''
    return WRITERS[kind](data)

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
    content = ''.join([gen_ast_node(e) for e in subs])
    return gen_tag(tag, content, attr, classes)

def gen_quote_tag(data):
    # 引用文本，需要区分单引号还是双引号
    quotetype, inlines = data
    quotetype = quotetype['t']
    content = ''.join([gen_ast_node(e) for e in inlines])
    if 'SingleQuote' == quotetype:
        return '&#145;' + content + '&#146;'
    elif 'DoubleQuote' == quotetype:
        return '&#147;' + content + '&#148;'

def gen_ordered_list(data):
    attrs, blocks = data
    num, style, delim = attrs
    print(num, style['t'], delim['t'])
    return '<ol>' + '</ol>'