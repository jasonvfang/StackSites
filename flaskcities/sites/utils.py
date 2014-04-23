import boto
import mimetypes
from urlparse import urljoin


def get_bucket():
    """Returns a boto Bucket object."""
    from flask import current_app
    access_key_id = current_app.config['AWS_ACCESS_KEY']
    secret = current_app.config['AWS_SECRET_KEY']
    bucket_name = current_app.config['BUCKET_NAME']
    conn = boto.connect_s3(access_key_id, secret)
    return conn.get_bucket(bucket_name)
    
    
def get_index(site):
    bucket = get_bucket()
    return make_s3_path(site, 'index.html')
    
    
def get_files(site):
    bucket = get_bucket()
    files = bucket.list(prefix='{0}/'.format(site))
    files = [make_s3_path(site, fname) for fname in files]
    return files
    
    
def upload_to_s3(file_obj, site, filename=None):
    """Uploads the file_obj to an Amazon S3 bucket under filename if specified."""
    if not filename:
        filename = werkzeug.secure_filename(file_obj.filename)
    filename = '{0}/{1}'.format(site, filename)
    mimetype = mimetypes.guess_type(filename)[0]
    bucket = get_bucket()
    key = bucket.new_key(filename)
    key.set_metadata('Content-Type', mimetype)
    file_obj.seek(0)
    key.set_contents_from_file(file_obj)
    key.set_acl('public-read')
    
    
def make_s3_path(site, filename):
    from flask import current_app
    app = current_app
    """Creates a string combining the standard S3 URL and a filename to make a valid link."""
    return urljoin('http://s3.amazonaws.com/{0}/{1}/'.format(app.config['BUCKET_NAME'], site),
                    filename)