import os
import boto
import ntpath
import mimetypes
import werkzeug
import requests
from urlparse import urljoin

from flask import current_app, abort
from flask.ext.login import current_user


def get_bucket(temp_bucket=False):
    """Returns a boto Bucket object."""
    from flask import current_app
    access_key_id = current_app.config['AWS_ACCESS_KEY']
    secret = current_app.config['AWS_SECRET_KEY']
    bucket_name = current_app.config['BUCKET_NAME']
    if temp_bucket:
        bucket_name = current_app.config['TEMP_BUCKET_NAME']
    conn = boto.connect_s3(access_key_id, secret)
    return conn.get_bucket(bucket_name)


def get_fname_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_file_ext(filename):
    return os.path.splitext(filename)[1].replace('.', '') or None


def get_keys(username, site_name, folder_prefix=None):
    bucket = get_bucket()
    prefix = "{0}/{1}".format(username, site_name)

    if folder_prefix is not None:
        keys = bucket.list(prefix=folder_prefix)
        max_slashes = folder_prefix.count('/')
        keys_in_folder = []
        for key in keys:
            last_slash = key.name.rfind('/')
            if key.name != folder_prefix and (key.name.count('/') == max_slashes or key.name[last_slash:] == '/'):
                keys_in_folder.append(key)
        return keys_in_folder

    keys = bucket.list(prefix=prefix)
    # if no folder_prefix, then return all the keys in the current folder
    return [key for key in keys if len(key.name.split('/')) < 4 or not key.name.split('/')[3]]


def get_files_data(username, site_name, folder_prefix=None):
    bucket = get_bucket()
    keys = get_keys(username, site_name, folder_prefix=folder_prefix)

    files = []

    for key in keys:

        key_data = {
            'name': get_fname_from_path(key.name),
            'size': key.size,
            'ext': get_file_ext(key.name),
            'is_folder': key.name[-1] == '/',
            'key': key.name
        }

        files.append(key_data)

    return files


def delete_site_from_s3(username, site_name):
    bucket = get_bucket()
    keys = get_keys(username, site_name)
    map(lambda key: key.delete(), keys)


def upload_index_for_new_site(username, site_name):
    index = current_app.open_resource('templates/new_site.html')
    upload_to_s3(index, username, site_name, 'index.html')


def upload_to_s3(file_obj, username, site_name, filename=None, set_contents_from_str=False):
    """Uploads the file_obj to an Amazon S3 bucket under filename if specified."""
    if not filename:
        filename = werkzeug.secure_filename(file_obj.filename)
    mimetype = mimetypes.guess_type(filename)[0]

    if '/' not in filename:
        filename = '{0}/{1}/{2}'.format(username, site_name, filename)

    bucket = get_bucket()
    key = bucket.new_key(filename)
    key.set_metadata('Content-Type', mimetype)

    if not set_contents_from_str:
        file_obj.seek(0)
        key.set_contents_from_file(file_obj)
    else:
        key.set_contents_from_string(file_obj)

    key.set_acl('public-read')


def update_temp_in_s3(temp_file_id, data):
    bucket = get_bucket(temp_bucket=True)
    fname = "{0}.html".format(temp_file_id)
    key = bucket.new_key(fname)
    mimetype = mimetypes.guess_type(fname)[0]
    key.set_metadata('Content-Type', mimetype)
    key.set_contents_from_string(data)
    key.set_acl('public-read')


def transfer_landing_demo(temp_file_id, username, site_name):
    temp_file_string_data = requests.get(make_s3_path_for_temp(temp_file_id)).content
    upload_to_s3(temp_file_string_data, username, site_name, 'index.html', True)


def make_s3_path_for_temp(temp_file_id):
    bucket = get_bucket(temp_bucket=True)
    protocol = 'http' if current_app.config['DEBUG'] else 'https'
    s3_path = "{0}://s3.amazonaws.com/{1}/{2}.html".format(protocol, current_app.config['TEMP_BUCKET_NAME'], temp_file_id)
    return s3_path


def make_s3_path(username, site_name, key):
    """Creates a string combining the standard S3 URL and a filename to make a valid link."""
    protocol = 'http' if current_app.config['DEBUG'] else 'https'
    if '/' in key:
        s3_path = "{0}://s3.amazonaws.com/{1}/{2}".format(protocol, current_app.config['BUCKET_NAME'], key)
    else:
        s3_path = "{0}://s3.amazonaws.com/{1}/{2}/{3}/{4}".format(protocol, current_app.config['BUCKET_NAME'], username, site_name, key)

    return s3_path


def delete_s3_file(username, site_name, key):
    bucket = get_bucket()
    key = bucket.lookup('/{}'.format(key))
    key.delete()


def create_folder_in_s3(username, site_name, folder_name, folder_key):
    bucket = get_bucket()
    key = bucket.new_key('{}/{}/'.format(folder_key, folder_name))
    key.set_contents_from_string('')
    key.set_acl('public-read')


def owns_site(site):
    if site is None:
        abort(404)

    if current_user != site.user:
        abort(403)
