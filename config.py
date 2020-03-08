#! env python

from datetime import date

SITENAME = 'szm.me'
AUTHOR   = 'Song Ziming'
SOURCE   = 'https://github.com/songziming/blog'

TIMEZONE = 'Asia/Shanghai'
THISYEAR = date.today().year

PATH        = 'content'
OUTPUT_PATH = 'output'
THEME       = 'theme'

# disable archive, categories, tags and authors
DIRECT_TEMPLATES = [ 'index' ]
CATEGORY_SAVE_AS = ''
AUTHOR_SAVE_AS   = ''
TAG_SAVE_AS      = ''

# disable feeds
FEED_ALL_ATOM         = None
CATEGORY_FEED_ATOM    = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM      = None
AUTHOR_FEED_RSS       = None
