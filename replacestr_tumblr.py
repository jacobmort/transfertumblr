# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 18:40:39 2017

@author: chris
"""

__author__ = 'jacob'
import pytumblr
import urllib
import os
import sys
from urlparse import urlparse
from os.path import splitext, basename

BLOGNAME = 'YOUR_BLOG.tumblr.com'
CLIENT = pytumblr.TumblrRestClient(
    'CONSUMER_KEY',
    'CONSUMER_SECRET',
    'OAUTH_TOKEN',
    'OAUTH_SECRET'
)
OLDSTR = '<OLD_STRING>'
NEWSTR = '<NEW_STRING>'

#pytumblr doesn't handle unicode well, convert to string
def encode_to_html(uni_str):
    return uni_str.encode('ascii', 'xmlcharrefreplace')


def get_filename(url):
    disassembled = urlparse(url)
    filename, file_ext = splitext(basename(disassembled.path))
    return filename + file_ext


def export_posts(client, from_blog):
    more = True
    offset = 0
    all_posts = []
    while more:
        new_posts = client.posts(from_blog, offset=offset)['posts']
        new_posts_len = len(new_posts)
        if new_posts_len > 0:
            offset += new_posts_len
            all_posts = all_posts + new_posts
        else:
            more = False
    return all_posts


def strreplace_posts(posts, client, to_blog, oldstr, newstr):
    for post in reversed(posts):
        try:
            params = {
            
            }
            
            if 'type' in post and post['type']:
                params['type'] = post['type']
            
            if 'caption' in post and post['caption']:
                captioninhtml = encode_to_html(post['caption']) 
                if captioninhtml.find(oldstr) == -1:
                    continue
                newcaptioninhtml = captioninhtml.replace(oldstr, newstr)
                params['caption'] = newcaptioninhtml
            elif 'body' in post and post['body']:
                bodyinhtml = encode_to_html(post['body']) 
                if bodyinhtml.find(oldstr) == -1:
                    continue
                newbodyinhtml = bodyinhtml.replace(oldstr, newstr)
                params['body'] = newbodyinhtml
            else:
                continue
                
            if 'id' in post and post['id']:
                params['id'] = post['id']

            if post['type'] == 'text' or post['type'] == 'photo' :
                client.edit_post(to_blog, **params)
                if 'title' in post and post['title']:
                    print(post['title'])
            else:
                print 'type not supported %s' % post['type']

        except:
            print "Unexpected error:", sys.exc_info()[0]
            print "%s" % post

def delete_posts(posts,client, blog_name):
    if blog_name == BLOGNAME:
        raise Exception('Are you sure you want to delete this?')
    for post in posts:
        client.delete_post(blog_name, post['id'])

all_posts = export_posts(CLIENT, BLOGNAME)
print(all_posts)
strreplace_posts(all_posts, CLIENT, BLOGNAME, OLDSTR, NEWSTR)
