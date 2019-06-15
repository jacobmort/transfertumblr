# -*- coding: utf-8 -*-

__author__ = 'jacob'
import pytumblr
import urllib.request
import os
import sys
from urllib.parse import urlparse
from os.path import splitext, basename

FROM_BLOG = 'releasemindjp.tumblr.com'
FROM_CLIENT = pytumblr.TumblrRestClient(
    'CONSUMER_KEY',
    'CONSUMER_SECRET',
    'OAUTH_TOKEN',
    'OAUTH_SECRET'
)

TO_BLOG = 'chrisfungky.tumblr.com'
TO_CLIENT = pytumblr.TumblrRestClient(
    'CONSUMER_KEY',
    'CONSUMER_SECRET',
    'OAUTH_TOKEN',
    'OAUTH_SECRET'
)

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


def import_posts(posts, client, to_blog):
    for post in reversed(posts):
        try:
            params = {
                'state': "private",
                'format': "html"
            }
            if 'caption' in post and post['caption']:
                params['caption'] = encode_to_html(post['caption'])

            if 'title' in post and post['title']:
                print(post['title'])
                params['title'] = encode_to_html(post['title'])

            if 'body' in post and post['body']:
                params['body'] = encode_to_html(post['body'])

            if post['date']:
                params['date'] = encode_to_html(post['date'])

            if post['slug']:
                params['slug'] = encode_to_html(post['slug'])

            if 'tags' in post and len(post['tags']) > 0:
                params['tags'] = post['tags']

            if post['type'] == 'photo':
                if len(post['photos']) == 1:
                    params['source'] = post['photos'][0]['original_size']['url']
                    client.create_photo(to_blog, **params)
                else: #photo set
                    files = []
                    for photo in post['photos']:
                        url = photo['original_size']['url']
                        file_name = get_filename(url)
                        f = open(file_name, 'wb')
                        f.write(urllib.request.urlopen(url).read())
                        f.close()
                        files.append(encode_to_html(os.path.realpath(f.name)))
                    params['data'] = files
                    client.create_photo(to_blog, **params)
                    for removeFile in files:
                        os.remove(removeFile)

            elif post['type'] == 'video':
                params['embed'] = post['player'][0]['embed_code']
                client.create_video(to_blog, **params)

            elif post['type'] == 'text':
                client.create_text(to_blog, **params)
            else:
                print ('type not supported %s' % post['type'])

        except:
            print ("Unexpected error:", sys.exc_info()[0])
            print ("%s" % post)

def delete_posts(posts,client, blog_name):
    if blog_name == FROM_BLOG:
        raise Exception('Are you sure you want to delete this?')
    for post in posts:
        client.delete_post(blog_name, post['id'])

all_posts = export_posts(FROM_CLIENT, FROM_BLOG)
print(all_posts)
import_posts(all_posts, TO_CLIENT, TO_BLOG)