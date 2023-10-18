#! env python

from pandocfilters import toJSONFilter, walk

def processNode(key, value, format, meta):
    if key=='Header':
        print(f'header level {value[0]}, content {value[2]}')

if __name__ == "__main__":
    # toJSONFilter(processNode)
    walk()