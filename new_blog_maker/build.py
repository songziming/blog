#! env python

'''
静态网站构建脚本
'''

import os
import glob
import json

import subprocess



# 运行 pandoc 将 markdown 转换为 html，输出的 html 里面还有元数据
def run_pandoc(src):
    cmd = ['pandoc', '-f', 'markdown', '-t', 'html5', '--toc', '--template', 'template.html', src]
    res = subprocess.run(cmd, capture_output=True)
    return res.stdout.decode('utf-8')


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



def main():
    posts = glob.glob('posts/*.md')
    for post in posts:
        convert_file(post)



if '__main__' == __name__:
    main()
