#! env python

'''
静态网站生成器 2.0 (WIP)
'''

import os
import glob
import subprocess


'''
每个输出文件都是一个 Item，分多种类型，生成逻辑各不相同

每个 Item 都有自己的生成管线，管线包括许多 step，每个 step 能访问不同的全局数据

Item 自动判断缓存是否过期，只有过期的 Item 才需要构建，模仿 GNU Make

网站就是很多 Item，Item 信息主要来自一个文件，部分信息来自其他 Item（修正 url、站内链接、静态资源引用）
输出文件名和内容不仅取决于输入文件，不能像 Makefile 一样仅根据时间戳判断是否失效。
我们需要将上一次的编译缓存保存为 JSON，类似于 GCC 自动生成依赖文件。
'''


# 代表输出目录下的一个文件
class Item:
    def __init__(self):
        self.source = None  # 输入文件路径，可以为空
        self.target = []

    def get_file(self):
        # 返回相对于输出目录的路径
        return os.path.join(self.target)

    def get_link(self):
        # 返回网址链接，一般和 target 相同，可以省去最后的 index.html
        if 'index.html' == self.target[-1]:
            return '/'.join([''] + self.target[:-1] + [''])
        else:
            return '/'.join([''] + self.target)

    def get_deps(self):
        # 返回依赖的文件列表，第一个文件是主要输入
        return []



'''
TextItem                输出一个文本文件，内容由 text() 决定
TemplateItem(TextItem)  输出文本文件，内容是 Jinja 模板渲染生成的，输入主体 html 和数据字典
'''



# 凭空生成的文件，纯文本
class TextItem(Item):
    def __init__(self, text=''):
        self.text = text

    # @override
    def build(self, output_dir):
        file = os.path.join(output_dir, self.get_file())
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, 'w') as f:
            f.write(self.text)


class SimpleTextItem(TextItem):
    def __init__(self, text=''):
        self.text = text
    def text(self):
        return self.text


class CssItem(TextItem):
    def text(self):
        res = subprocess.run(['csso', self.source])
        return res.stdout.decode()






if '__main__' == __name__:
    post_dir = 'posts'

    post_files = glob.glob(os.path.join(post_dir, '**', '*.md'), recursive=True)
    pass
