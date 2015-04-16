# -*- coding: utf-8 -*-

from flask import Flask, render_template, request
from post import get_posts_list, get_post_content
from mobile.sniffer.detect import detect_mobile_browser

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

blog = Flask(__name__)
posts_dir = 'posts'

def is_mobile_request():
    ua = request.user_agent.string
    if ua and detect_mobile_browser(ua):
        return True
    else:
        return False

@blog.route('/')
def index():
    mobile = 'mobile_' if is_mobile_request() else ''
    return render_template('index.html',
            mobile = mobile, posts = get_posts_list(posts_dir))

@blog.route('/posts/<year>/<month>/<day>/<post_name>/')
def post(year, month, day, post_name):
    post_time = year + '-' + month + '-' + day
    content = get_post_content(posts_dir, post_time, post_name)
    if content:
        mobile = 'mobile_' if is_mobile_request() else ''
        return render_template('post.html',
                mobile = mobile, title = post_name,
                time = post_time, content = content)
    else:
        return render_template('404.html'), 404

@blog.route('/about.html')
def about():
    mobile = 'mobile_' if is_mobile_request() else ''
    return render_template('about.html', mobile = mobile)

@blog.route('/<css_file>.css')
def css(css_file):
    return blog.send_static_file(css_file + '.css')

@blog.route('/images/<image_file>')
def image(image_file):
    return blog.send_static_file('images/' + image_file)

@blog.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    blog.run(host = '0.0.0.0', port = 80)
