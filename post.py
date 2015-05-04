# -*- coding: utf-8 -*-

import os
import re
import StringIO
import markdown
import datetime

md_pattern = re.compile('^(\d+)-(\d+)-(\d+)-(.+)\.md$')

def get_posts_list(dir):
    return map(lambda m : {
        'href' : dir + '/' + m.group(1) + '/' + m.group(2) + '/' + m.group(3) + '/' + m.group(4) + '/',
        'caption' : m.group(4),
        'post_time' : m.group(1) + '-' + m.group(2) + '-' + m.group(3),
        'date_time' : datetime.datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        },
        filter(lambda m : m != None, map(md_pattern.match, sorted(os.listdir(dir), reverse = True))))

def get_post_content(dir, post_time, post_name):
    file_name = dir + '/' + post_time + '-' + post_name + '.md'
    if not os.path.exists(file_name):
        return None
    output = StringIO.StringIO()
    markdown.markdownFromFile(input = file_name, output = output, extensions = ['markdown.extensions.tables'])
    content = output.getvalue()
    output.close()
    return content
