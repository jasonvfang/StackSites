import boto
import ntpath
import mimetypes
from urlparse import urljoin

from flask import current_app


def get_bucket():
    """Returns a boto Bucket object."""
    from flask import current_app
    access_key_id = current_app.config['AWS_ACCESS_KEY']
    secret = current_app.config['AWS_SECRET_KEY']
    bucket_name = current_app.config['BUCKET_NAME']
    conn = boto.connect_s3(access_key_id, secret)
    return conn.get_bucket(bucket_name)


def get_fname_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_files_data(username, site_name):
    bucket = get_bucket()
    keys = bucket.list(prefix="{0}/{1}".format(username, site_name))
    return [{'name': get_fname_from_path(key.name), 'size': key.size} for key in keys]
    
    
def upload_index_for_new_site(username, site_name):
    index = current_app.open_resource('templates/new_site.html')
    upload_to_s3(index, username, site_name, 'index.html')
    
    
def upload_to_s3(file_obj, username, site_name, filename=None):
    """Uploads the file_obj to an Amazon S3 bucket under filename if specified."""
    if not filename:
        filename = werkzeug.secure_filename(file_obj.filename)
    mimetype = mimetypes.guess_type(filename)[0]
    filename = '{0}/{1}/{2}'.format(username, site_name, filename)
    bucket = get_bucket()
    key = bucket.new_key(filename)
    key.set_metadata('Content-Type', mimetype)
    file_obj.seek(0)
    key.set_contents_from_file(file_obj)
    key.set_acl('public-read')
    
    
def make_s3_path(username, site_name, filename):
    """Creates a string combining the standard S3 URL and a filename to make a valid link."""
    s3_path = "http://s3.amazonaws.com/{0}/{1}/{2}/".format(current_app.config['BUCKET_NAME'], username, site_name)
    return urljoin(s3_path, filename)