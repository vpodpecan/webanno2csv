import os
from time import strftime
from hashlib import sha1
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import render_template, render_template_string

import convert


UPLOAD_FOLDER = os.path.abspath('uploads')
ALLOWED_EXTENSIONS = {'tsv'}
TERM_CAT_GEN_SENT_REL_file = 'TERM_CAT_GEN_SENT_REL.csv'
TERM_CATEGORY_file = 'TERM_CATEGORY.csv'
DEF_ELEMENTS_file = 'DEF_ELEMENTS.csv'
REL_REL_FRAME_file = 'REL_REL_FRAME.csv'


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.urandom(30)


def generate_id():
    s = strftime('%a-%d-%b-%Y-%H-%M-%S')
    return '%s--%s' % (s, sha1(s.encode()).hexdigest()[:5])


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return render_template('index.html', message="ERROR: your POST request has no file part!")
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', message="ERROR: please select a .tsv file.")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            tmpfolder = generate_id()
            folder = os.path.join(app.config['UPLOAD_FOLDER'], tmpfolder)
            os.mkdir(folder)
            fullfilename = os.path.join(folder, filename)
            file.save(fullfilename)

            # do the extraction
            datalines, groups = convert.read_data(fullfilename)
            convert.export_TERM_CAT_GEN_SENT_REL(datalines, os.path.join(folder, TERM_CAT_GEN_SENT_REL_file))
            convert.export_TERM_CATEGORY(datalines, os.path.join(folder, TERM_CATEGORY_file))
            convert.export_DEF_ELEMENTS(datalines, os.path.join(folder, DEF_ELEMENTS_file))
            convert.export_REL_REL_FRAME(datalines, groups, os.path.join(folder, REL_REL_FRAME_file))
            return render_template('results.html', tmpfolder=tmpfolder,
                                   results=[TERM_CAT_GEN_SENT_REL_file, TERM_CATEGORY_file, DEF_ELEMENTS_file, REL_REL_FRAME_file])
        else:
            return render_template('index.html', message="ERROR: only .tsv files are allowed.")
    else:
        return render_template('index.html')


@app.route('/uploads/<temp_folder>/<filename>')
def uploaded_file(filename, temp_folder):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'], temp_folder),
                               filename)
