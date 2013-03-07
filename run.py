import os
from datetime import datetime
import json
import random
import hashlib

from flask import Flask, render_template, request, redirect, url_for, \
        safe_join, flash
from werkzeug import secure_filename

import beanstalkc

app = Flask(__name__)
app.config.from_pyfile('settings.cfg')

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
    'uploads')
ALLOWED_EXTS = set([
    'txt', 'rtf',
    'pdf',
    'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
    'odf', 'odt', 'ods', 'odp',
    'csv',
    'zip', 'tar', 'bz2', '7zip', 'rar', 'gz',
])

def allowed_file(f):
    filename = f.filename
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTS

def get_upload_uid(filename, timestamp):
    """
    Returns a hash of the upload filename, current timestamp, and a random salt
    to be used as a unique ID for the upload
    """
    return hashlib.sha256( filename + timestamp + str(random.randint(0,
        65536))).hexdigest()

def handle_file_upload(request):
    '''
    Check that the file upload is valid, save the file to the filesystem,
    and add a job to the queue
    '''
    error = None
    safe_filename = None
    # DEBUG
    #print "Padding size: ", len(request.form['padding'])
    upload = request.files['file']
    if not upload:
        error = "No valid file specified (received no file data)"
    elif not allowed_file(upload):
        # TODO: DRY up (repeats code from allowed_file())
        file_type = upload.filename.rsplit('.', 1)[1]
        error = "Filetype .%s is not allowed." % file_type
    else:
        # Avoid various attacks by sanizing the filename
        safe_filename = secure_filename(upload.filename)
        # If the safe filename is empty, generate a random filename
        if safe_filename == '':
            # Use the time of upload with a random number to avoid collisions
            # (however unlikely)
            safe_filename = 'honest_upload_%s_%s' % (
                    datetime.now().isoformat(),
                    random.randint(0, 1024))
        safe_path = safe_join(UPLOAD_FOLDER, safe_filename)
        upload.save(safe_path)
        timestamp = datetime.now()
        upload_uid = get_upload_uid(safe_filename, str(timestamp))
        upload_info = {
                'filename':     safe_filename,
                'path':         safe_path,
                'uid':          upload_uid,
                'timestamp':    str(timestamp), # can't json-encode datetime
                'comment':      request.form['comment']
            }
        beanstalk = beanstalkc.Connection(host='localhost', port=11300)
        beanstalk.put(json.dumps(upload_info))
        beanstalk.close()

    return error, safe_filename, upload_uid

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    '''
    Provide a form for file uploads. Save the file to disk, and add a job to
    the beanstalk work queue to process it.
    '''
    if request.method == 'POST':
        upload_handling_error, safe_filename, upload_uid \
                = handle_file_upload(request)
        if upload_handling_error:
            flash('Error: ' + upload_handling_error, 'error')
        else:
            flash('%s uploaded successfully.' % safe_filename, 'success')
            flash('Your upload ID is %s' % upload_uid, 'success')
        return redirect(url_for('upload'))
    return render_template('upload.html')

@app.route('/')
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()
